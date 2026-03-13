import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from .model import PneumoniaModel
from .schemas import PredictionResponse
from .config import settings

# --- 1. Dynamic Paths Setup (Fixes the 404 errors) ---
BASE_DIR = Path(__file__).resolve().parent

model_instance: PneumoniaModel | None = None

# --- 2. Lifespan for Model Loading ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_instance
    try:
        model_instance = PneumoniaModel(settings.model_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load model: {e}")
    yield
    # Any teardown logic (e.g., clearing memory) would go here

# --- 3. SINGLE App Initialization ---
app = FastAPI(title="Pneumonia X-ray Classifier", version="1.0.0", lifespan=lifespan)

# --- 4. CORS Middleware (Fixed Typo) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]  # Fixed from allow_heads
)

# --- 5. Mount Static & Templates ---
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


# --- 6. Routes ---
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