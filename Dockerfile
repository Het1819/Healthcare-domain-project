# ---- Base image ----
FROM python:3.11-slim

# # ---- System deps (opencv runtime libs) ----
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libgl1 \
#     libglib2.0-0 \
#     && rm -rf /var/lib/apt/lists/*

# ---- Workdir ----
WORKDIR /app

# ---- Python env ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---- Install deps first (better layer caching) ----
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy application code + model ----
COPY app /app/app
COPY models /app/models
COPY README.md /app/README.md

# ---- Expose port ----
EXPOSE 8000

# ---- Run with uvicorn ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]