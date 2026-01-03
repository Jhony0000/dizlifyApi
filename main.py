from fastapi import FastAPI
from pydantic import BaseModel
from nsfw_detector import predict
from PIL import Image
import requests
from io import BytesIO
import os
import cv2

app = FastAPI()

print("Current working dir:", os.getcwd())

# ================= Load NSFW Model =================
model = predict.load_model("mobilenet_v2_140_224")
print("NSFW Model Loaded Successfully")

# ================= Request Model =================
class Media(BaseModel):
    url: str
    type: str  # "image" or "video"

# ================= NSFW Scoring =================
def nsfw_score_image(img_path: str):
    result = predict.classify(model, img_path)
    scores = result[img_path]
    
    print(f"DEBUG - {img_path} Scores:", scores)

    porn = scores.get("porn", 0)
    sexy = scores.get("sexy", 0)
    hentai = scores.get("hentai", 0)
    max_score = max(porn, sexy, hentai)

    return {
        "porn": porn,
        "sexy": sexy,
        "hentai": hentai,
        "max": max_score
    }

# ================= Moderate Endpoint =================
@app.post("/moderate")
def moderate(media: Media):
    try:
        # ---------------- IMAGE ----------------
        if media.type == "image":
            response = requests.get(media.url, timeout=10)
            img = Image.open(BytesIO(response.content)).convert("RGB")

            img_path = "temp.jpg"
            img.save(img_path, "JPEG")

            scores = nsfw_score_image(img_path)

            # Delete temp file
            if os.path.exists(img_path):
                os.remove(img_path)

            if scores["max"] > 0.5:
                print("Adult image detected. Rejecting...")
                return {
                    "status": "rejected",
                    "reason": "NSFW image detected",
                    "scores": scores
                }

            return {
                "status": "approved",
                "scores": scores
            }

        # ---------------- VIDEO ----------------
        elif media.type == "video":
            # Download video
            video_path = "temp_video.mp4"
            r = requests.get(media.url, stream=True)
            with open(video_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    f.write(chunk)

            cap = cv2.VideoCapture(video_path)
            max_score = 0
            frames_checked = 0

            while cap.isOpened() and frames_checked < 12:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_path = f"frame_{frames_checked}.jpg"
                cv2.imwrite(frame_path, frame)

                scores = nsfw_score_image(frame_path)
                max_score = max(max_score, scores["max"])

                # Delete temp frame
                if os.path.exists(frame_path):
                    os.remove(frame_path)

                frames_checked += 1

                if max_score > 0.5:
                    cap.release()
                    if os.path.exists(video_path):
                        os.remove(video_path)
                    print("Adult video detected. Rejecting...")
                    return {
                        "status": "rejected",
                        "reason": "NSFW video detected",
                        "risk": int(max_score * 100)
                    }

            cap.release()
            if os.path.exists(video_path):
                os.remove(video_path)

            return {
                "status": "approved",
                "risk": int(max_score * 100)
            }

        else:
            return {"status": "review", "risk": 50}

    except Exception as e:
        print("Error:", e)
        return {"status": "review", "error": str(e)}
