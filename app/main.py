from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .model import PneumoniaModel
from .schemas import PredictionResponse
from .config import settings

app = FastAPI(title="Pneumonia X-ray Classifier", version="1.0.0")

# --- Frontend wiring (templates + static) ---
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

model_instance: PneumoniaModel | None = None


@app.on_event("startup")
def load_ml_model():
    global model_instance
    try:
        model_instance = PneumoniaModel(settings.model_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {e}")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """
    Simple beautiful web UI (same backend, no separate frontend server).
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "default_threshold": settings.threshold,
            "img_size": settings.img_size,
        },
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model_instance is not None,
        "img_size": settings.img_size,
        "threshold": settings.threshold,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(
    file: UploadFile = File(...),
    threshold: float | None = Query(default=None, ge=0.0, le=1.0),
):
    if model_instance is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    # Basic content-type check (not perfect, but helpful)
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "application/octet-stream"]:
        raise HTTPException(status_code=400, detail=f"Unsupported content_type: {file.content_type}")

    try:
        image_bytes = await file.read()
        x = model_instance.preprocess_bytes(image_bytes)
        result = model_instance.predict(x, threshold=threshold)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")