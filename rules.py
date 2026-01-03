from utils.media_check import detect_adult_image

BLOCKED_WORDS = ["xxx", "porn", "sex", "nude", "hot"]

def calculate_risk(media):
    """
    media = {
      "url": "...",
      "type": "image" | "video"
    }
    """

    # 🔴 Instant reject by keyword
    if any(word in media["url"].lower() for word in BLOCKED_WORDS):
        return 100

    risk = 0

    if media["type"] == "video":
        risk += 20

    if media["type"] == "image":
        if detect_adult_image(media["url"]):
            return 100   # 🔥 direct reject

    return risk
