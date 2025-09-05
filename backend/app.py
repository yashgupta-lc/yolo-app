from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
from ultralytics import YOLO
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    model = YOLO("yolov8n.pt")  # tiny YOLO model for speed
    logger.info("YOLO model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load YOLO model: {e}")
    raise

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        # Read file
        contents = await file.read()
        logger.info(f"Received file: {file.filename}, size: {len(contents)} bytes")

        # Convert to numpy array
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image")
            return JSONResponse({"error": "Failed to decode image"}, status_code=400)

        # Run YOLO
        results = model(img)
        logger.info("YOLO detection completed")

        # Draw bounding boxes
        annotated = results[0].plot()

        # Encode image back to base64
        _, buffer = cv2.imencode(".jpg", annotated)
        if not _:
            logger.error("Failed to encode result image")
            return JSONResponse({"error": "Failed to encode result image"}, status_code=500)
            
        img_str = base64.b64encode(buffer).decode("utf-8")
        logger.info("Successfully processed image")

        return JSONResponse({"image": img_str})

    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)