from pydantic import BaseModel

class Settings(BaseModel):
    model_path: str = "models/pneumonia_model.keras"
    img_size: int = 150
    threshold: float = 0.5  # default decision threshold

settings = Settings()