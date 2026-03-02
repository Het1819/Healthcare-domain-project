import numpy as np
import cv2
from tensorflow.keras.models import load_model
from .config import settings

LABELS = ["PNEUMONIA", "NORMAL"]  # 0 -> PNEUMONIA, 1 -> NORMAL if you trained that way

class PneumoniaModel:
    def __init__(self, model_path: str):
        self.model = load_model(model_path)

    def preprocess_bytes(self, image_bytes: bytes) -> np.ndarray:
        # Decode bytes -> image (OpenCV)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Invalid image file or unsupported format.")

        img = cv2.resize(img, (settings.img_size, settings.img_size))
        img = img.astype("float32") / 255.0
        img = np.expand_dims(img, axis=-1)  # (H,W,1)
        img = np.expand_dims(img, axis=0)   # (1,H,W,1)
        return img

    def predict(self, x: np.ndarray, threshold: float | None = None) -> dict:
        thr = settings.threshold if threshold is None else float(threshold)

        # Model outputs sigmoid probability for class 1 (NORMAL) in many binary setups
        prob_normal = float(self.model.predict(x, verbose=0)[0][0])
        prob_pneumonia = 1.0 - prob_normal

        pred = 1 if prob_normal >= thr else 0
        return {
            "pred_label": LABELS[pred],
            "prob_normal": prob_normal,
            "prob_pneumonia": prob_pneumonia,
            "threshold": thr,
        }