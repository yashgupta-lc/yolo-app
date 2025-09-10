# YOLO Object Detection App

A full-stack web application for real-time object detection using YOLO (You Only Look Once) model. The app consists of a FastAPI backend for image processing and a React frontend with nginx for serving static files.

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Clone or download the project**
   ```bash
   # If you have the project files, navigate to the project directory
   cd /path/to/YOLO-APP
   ```

2. **Start the application**
   ```bash
   # Start both backend and frontend services
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:7070
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Manual Docker Setup

#### Backend Setup
```bash
# Terminal 1 - Backend
cd backend
docker build -t yolo-backend .
docker run -p 8000:8000 yolo-backend
```

#### Frontend Setup
```bash
# Terminal 2 - Frontend
cd frontend
docker build -t yolo-frontend .
docker run -p 7070:7070 yolo-frontend
```

## 📁 Project Structure
```
YOLO-APP/
├── backend/
│   ├── Dockerfile          # Python FastAPI container
│   ├── app.py             # Main FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── yolov8n.onnx      # YOLO model file
├── frontend/
│   ├── Dockerfile         # Multi-stage build with nginx
│   ├── package.json       # Node.js dependencies
│   ├── src/
│   │   ├── App.js        # Main React component
│   │   └── App.css       # Styling
│   └── public/           # Static assets
└── docker-compose.yml    # Orchestration file
```

## 🏗️ Architecture

### Backend (FastAPI)
- **Port**: 8000
- **Framework**: FastAPI with Uvicorn
- **Model**: YOLOv8 ONNX format
- **Features**: 
  - Image upload endpoint
  - Object detection processing
  - Base64 image response

### Frontend (React + Nginx)
- **Port**: 7070
- **Framework**: React 19 with Create React App
- **Server**: Nginx 1.27.4
- **Features**:
  - Image upload interface
  - Real-time processing feedback
  - Results display

## 🔧 Configuration

### Backend Configuration
The backend automatically loads the YOLO model (`yolov8n.onnx`) on startup. Make sure this file exists in the backend directory.

### Frontend Configuration
The frontend is configured to connect to the backend at `http://localhost:8000`. For production deployment, update the API URL in `src/App.js`.

## 🐳 Docker Details

### Backend Dockerfile
- **Base Image**: Python 3.9
- **Dependencies**: Installed from requirements.txt
- **Model**: YOLOv8 ONNX model included
- **Port**: 8000

### Frontend Dockerfile (Multi-stage)
- **Build Stage**: Node.js 23.11.0-slim
  - Installs dependencies
  - Builds React app for production
  - Creates optimized static files in `build/` directory
- **Runtime Stage**: Nginx 1.27.4
  - Serves static files from `/usr/share/nginx/html`
  - Configured to listen on port 7070
  - Optimized for production deployment

## 🚀 Deployment

### Development
```bash
# Start with hot reload
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Production
The frontend is already optimized for production with:
- Minified JavaScript and CSS
- Optimized static assets
- Nginx serving static files
- Ready for CloudFront CDN deployment

## 🔍 Usage

1. **Upload Image**: Click "Choose File" and select an image
2. **Process**: Click "Upload and Detect" to run object detection
3. **View Results**: The processed image with bounding boxes will appear below

