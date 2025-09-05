# YOLO Object Detection App Setup Guide

## Project Creation

### Step 1: Frontend Setup with Create React App
```bash
# Go to Desktop and create React app
cd /home/yash/Desktop
npx create-react-app YOLO-APP/frontend
```

### Step 2: Clone Your Repo
```bash
# Go back to YOLO-APP root
cd YOLO-APP

# Clone your repo (contains backend and extra files)
git clone https://github.com/yashgupta-lc/yolo-app.git temp-repo
```

### Step 3: Move Files Into Place
```bash
# Move backend into main directory
mv temp-repo/backend ./backend

# Move frontend Dockerfile
mv temp-repo/Dockerfile ./frontend/Dockerfile

# Move React files (overwrite existing ones)
mv -f temp-repo/App.js ./frontend/src/App.js
mv -f temp-repo/App.css ./frontend/src/App.css

# Move README (optional)
mv temp-repo/Readme.md ./Readme.md
```

### Step 4: Cleanup
```bash
rm -rf temp-repo
```

---

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
    │   ├── App.js   # replaced from repo
    │   ├── App.css  # replaced from repo
    │   └── index.js
    └── public/
```

---

## Backend Setup

### Building & Running Backend
```bash
# Terminal 1
cd /home/yash/Desktop/YOLO-APP/backend
docker build -t yolo-backend .
docker run -p 8000:8000 yolo-backend
```

---

## Frontend Setup 

### Building & Running Frontend
```bash
# Terminal 2
cd /home/yash/Desktop/YOLO-APP/frontend
docker build -t yolo-frontend .
docker run -p 3000:3000 yolo-frontend
```

---

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
- If backend can’t load YOLO model, check if `yolov8n.pt` exists in backend directory  
- If frontend shows "Failed to fetch", ensure backend is running and URL is correct  
- If changes aren’t reflecting, rebuild containers with:
```bash
docker build -t yolo-backend . # for backend
docker build -t yolo-frontend . # for frontend
```

---

## Accessing the App
- Frontend: http://localhost:3000  
- Backend API: http://localhost:8000  

---

## Development Tips
- Backend logs will show in Terminal 1  
- Frontend logs will show in Terminal 2  
- Use `docker logs <container-id>` to see logs of specific container  
- Use `docker exec -it <container-id> bash` to access container shell  
