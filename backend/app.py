from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
import cv2

from detector.eye_tracker import EyeTracker

app = FastAPI(title="Sleep Monitor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

eye_tracker = EyeTracker()

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.post("/predict-frame")
async def predict_frame(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return JSONResponse(content={"error": "No se pudo decodificar el frame"}, status_code=400)
        
        result = eye_tracker.analyze_frame(frame)

        return JSONResponse(content=result, status_code=200)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise JSONResponse(content={"error": str(e)}, status_code=500)