FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (so Docker can cache pip install layer)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir python-multipart

RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

COPY . .

# Fix Ultralytics config warning
ENV YOLO_CONFIG_DIR=/app/.config

# Expose backend port
EXPOSE 8000

# Start FastAPI with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
