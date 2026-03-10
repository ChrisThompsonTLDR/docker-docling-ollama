FROM python:3.12-slim

WORKDIR /app

# Docling needs libxcb, libGL, and libglib for headless rendering (matplotlib, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxcb1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# CPU-only torch + docling with RapidOCR + picture description (Ollama API)
# PictureDescriptionApiOptions uses remote API; no [vlm] local inference needed
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    "docling[rapidocr]" \
    fastapi uvicorn

COPY extract.py app.py /app/

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
