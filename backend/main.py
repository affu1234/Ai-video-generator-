from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Frontend connectivity ke liye CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "AI Video Generator Backend Working 🚀"}

@app.get("/generate-script")
def generate_script(prompt: str):
    return {
        "prompt": prompt,
        "script": f"Scene 1: Intro for {prompt}. Scene 2: Detailed explanation.",
        "status": "success"
    }
