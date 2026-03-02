from pydantic import BaseModel

class PredictionResponse(BaseModel):
    pred_label: str
    prob_normal: float
    prob_pneumonia: float
    threshold: float