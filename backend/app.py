from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
import onnxruntime as ort
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize ONNX Runtime session
ort_session = ort.InferenceSession("yolov8n.onnx")
input_name = ort_session.get_inputs()[0].name

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7070", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Preprocess function
def preprocess_image(img):
    # Resize image to model's expected sizing
    img = cv2.resize(img, (640, 640))
    
    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Normalize pixel values to [0, 1]
    img = img.astype(np.float32) / 255.0
    
    # Add batch dimension and transpose to NCHW format
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)
    
    return img

# Non-Maximum Suppression function
def nms(boxes, scores, iou_threshold=0.5):
    if len(boxes) == 0:
        return []
    
    # Sort by confidence scores
    indices = np.argsort(scores)[::-1]
    keep = []
    
    while len(indices) > 0:
        # Pick the box with highest confidence
        current = indices[0]
        keep.append(current)
        
        if len(indices) == 1:
            break
            
        # Calculate IoU with remaining boxes
        current_box = boxes[current]
        remaining_boxes = boxes[indices[1:]]
        
        # Calculate intersection
        x1 = np.maximum(current_box[0], remaining_boxes[:, 0])
        y1 = np.maximum(current_box[1], remaining_boxes[:, 1])
        x2 = np.minimum(current_box[2], remaining_boxes[:, 2])
        y2 = np.minimum(current_box[3], remaining_boxes[:, 3])
        
        intersection = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
        
        # Calculate areas
        current_area = (current_box[2] - current_box[0]) * (current_box[3] - current_box[1])
        remaining_areas = (remaining_boxes[:, 2] - remaining_boxes[:, 0]) * (remaining_boxes[:, 3] - remaining_boxes[:, 1])
        
        # Calculate IoU
        union = current_area + remaining_areas - intersection
        iou = intersection / union
        
        # Keep boxes with IoU less than threshold
        indices = indices[1:][iou <= iou_threshold]
    
    return keep

# Postprocess function
def postprocess_output(output, img_shape):
    # Get predictions from ONNX output
    predictions = np.squeeze(output[0]).T
    
    # Filter out low confidence detections
    confidence_threshold = 0.5
    scores = np.max(predictions[:, 4:], axis=1)
    predictions = predictions[scores > confidence_threshold, :]
    scores = scores[scores > confidence_threshold]
    
    if len(scores) == 0:
        return []
        
    # Get the class with the highest confidence
    class_ids = np.argmax(predictions[:, 4:], axis=1)
    
    # Get bounding boxes in original image size
    boxes = predictions[:, :4]
    
    # Rescale boxes to original image size
    input_shape = np.array([640, 640, 640, 640])
    img_shape = np.array([img_shape[1], img_shape[0], img_shape[1], img_shape[0]])
    boxes = np.divide(boxes, input_shape, dtype=np.float32)
    boxes = np.multiply(boxes, img_shape, dtype=np.float32)
    
    # Convert to x1, y1, x2, y2 format
    x1 = boxes[:, 0] - boxes[:, 2] / 2
    y1 = boxes[:, 1] - boxes[:, 3] / 2
    x2 = boxes[:, 0] + boxes[:, 2] / 2
    y2 = boxes[:, 1] + boxes[:, 3] / 2
    
    # Stack boxes for NMS
    boxes_nms = np.column_stack([x1, y1, x2, y2])
    
    # Apply Non-Maximum Suppression
    keep_indices = nms(boxes_nms, scores, iou_threshold=0.5)
    
    # Return only the kept detections
    if len(keep_indices) == 0:
        return []
    
    return [(x1[i], y1[i], x2[i], y2[i], scores[i], class_ids[i]) for i in keep_indices]

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

        # Preprocess image
        input_tensor = preprocess_image(img)
        
        # Run inference
        outputs = ort_session.run(None, {input_name: input_tensor})
        
        # Postprocess results
        detections = postprocess_output(outputs, img.shape)
        
        # Draw bounding boxes
        annotated_img = img.copy()
        
        # COCO class names (first 20 classes)
        class_names = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
            'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
            'dog', 'horse', 'sheep', 'cow'
        ]
        
        for x1, y1, x2, y2, score, class_id in detections:
            color = (0, 255, 0)  # Green color for boxes
            thickness = 2
            
            # Draw rectangle
            cv2.rectangle(annotated_img, (int(x1), int(y1)), (int(x2), int(y2)), color, thickness)
            
            # Prepare label
            class_name = class_names[int(class_id)] if int(class_id) < len(class_names) else f"Class {int(class_id)}"
            label = f"{class_name}: {float(score):.2f}"
            
            # Get text size for background rectangle
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            text_thickness = 1
            (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, text_thickness)
            
            # Draw background rectangle for text
            cv2.rectangle(annotated_img, 
                         (int(x1), int(y1) - text_height - 10), 
                         (int(x1) + text_width, int(y1)), 
                         color, -1)
            
            # Draw text
            cv2.putText(annotated_img, label, (int(x1), int(y1) - 5),
                       font, font_scale, (0, 0, 0), text_thickness)
        
        # Convert image to base64
        _, buffer = cv2.imencode(".jpg", annotated_img)
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