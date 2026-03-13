from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_path: str = "models/pneumonia_model.keras"
    img_size: int = 150
    threshold: float = 0.5  # default decision threshold

    class Config:
        # This allows Docker/Env vars to override defaults
        env_file = ".env" 

settings = Settings()

# from pydantic import BaseModel

# class Settings(BaseModel):
#     model_path: str = "models/pneumonia_model.keras"
#     img_size: int = 150
#     threshold: float = 0.5  # default decision threshold

# settings = Settings()
