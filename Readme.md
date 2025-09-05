# YOLO Object Detection App Setup Guide

## Project Creation

### Frontend Setup with Create React App
```bash
# Create a new React application
cd /home/yash/Desktop
npx create-react-app YOLO-APP/frontend
```

## Directory Structure
```
YOLO-APP/
├── backend/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
└── frontend/               # Created using create-react-app
    ├── Dockerfile
    ├── package.json
    ├── src/
    │   ├── App.js
    │   └── App.css
    └── public/
```

## Backend Setup

### Backend Dockerfile
```dockerfile
# filepath: /home/yash/Desktop/YOLO-APP/backend/Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

This Dockerfile:
- Uses Python 3.9 base image
- Sets working directory to /app
- Installs Python dependencies
- Copies all backend files
- Exposes port 8000
- Starts FastAPI server

### Building & Running Backend
```bash
# Terminal 1
cd /home/yash/Desktop/YOLO-APP/backend
docker build -t yolo-backend .
docker run -p 8000:8000 yolo-backend
```

## Frontend Setup 

### Frontend Dockerfile
```dockerfile
# filepath: /home/yash/Desktop/YOLO-APP/frontend/Dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

This Dockerfile:
- Uses Node.js 18 base image
- Sets working directory to /app
- Installs npm dependencies
- Copies all frontend files
- Exposes port 3000
- Starts React development server

### Building & Running Frontend
```bash
# Terminal 2
cd /home/yash/Desktop/YOLO-APP/frontend
docker build -t yolo-frontend .
docker run -p 3000:3000 yolo-frontend
```

## Troubleshooting

### Port Already in Use
If you get "port is already allocated" error:

1. Find containers using ports:
```bash
docker ps
```

2. Stop specific container:
```bash
docker stop <container-id>
```

3. Stop all running containers:
```bash
docker stop $(docker ps -q)
```

### Common Issues
- If backend can't load YOLO model, check if `yolov8n.pt` exists in backend directory
- If frontend shows "Failed to fetch", ensure backend is running and URL is correct
- If changes aren't reflecting, rebuild containers with:
```bash
docker build -t yolo-backend . # for backend
docker build -t yolo-frontend . # for frontend
```

## Accessing the App
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Development Tips
- Backend logs will show in Terminal 1
- Frontend logs will show in Terminal 2
- Use `docker logs <container-id>` to see logs of specific container
- Use `docker exec -it <container-id> bash` to access container shell