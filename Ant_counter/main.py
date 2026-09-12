from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from detect import detect_ants

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Ant Traffic Counter API is running"
    }

@app.get("/detect")
def run_detection():
    result = detect_ants()
    return result