from nsfw_detector import predict

MODEL_PATH = "models/nsfw_mobilenet2.224x224.h5"

model = predict.load_model(MODEL_PATH)

def detect_adult_image(image_path: str) -> bool:
    """
    Return True if image is adult
    """
    result = predict.classify(model, image_path)
    score = result[image_path]

    porn_score = score.get("porn", 0) + score.get("sexy", 0)

    return porn_score > 0.7
