from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "AI Video Generator Backend Working Perfectly! 🚀"}

@app.get("/generate-script")
def generate_script(prompt: str = ""):
    return {
        "prompt": prompt,
        "script": f"Scene 1: Introduction for {prompt}. Scene 2: Main explanation.",
        "status": "success"
    }
