from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai
import urllib.parse
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

stats_counter = {
    "total_generations": 610,
    "images_generated": 580,
    "prompts_enhanced": 390
}

@app.get("/")
def home():
    return {"status": "LuminaAI Elite Engine Active 🚀"}

@app.get("/get-stats")
def get_stats():
    return {
        "total": stats_counter["total_generations"],
        "images": stats_counter["images_generated"],
        "prompts": stats_counter["prompts_enhanced"]
    }

@app.get("/enhance-prompt")
def enhance_prompt(prompt: str = ""):
    if not prompt:
        return {"enhanced_prompt": prompt}
    
    enhanced = f"A masterpiece ultra-realistic cinematic 8k portrait of {prompt}, dramatic volumetric studio lighting, hyperdetailed render"
    if client:
        try:
            ai_prompt = f"Expand this into an ultra-luxury premium 8K visual image prompt in 1 concise line: '{prompt}'."
            res = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=ai_prompt,
            )
            if res.text:
                enhanced = res.text.strip()
        except Exception:
            pass
    
    stats_counter["prompts_enhanced"] += 1
    return {"enhanced_prompt": enhanced}

@app.get("/generate-visual")
def generate_visual(prompt: str = "", aspect_ratio: str = "16:9"):
    if not prompt:
        return {"error": "Prompt is required"}

    stats_counter["total_generations"] += 1
    stats_counter["images_generated"] += 1

    w, h = 1280, 720
    if aspect_ratio == "9:16":
        w, h = 720, 1280
    elif aspect_ratio == "1:1":
        w, h = 800, 800

    # Clean prompt for URL encoding so exact words pass to Pollinations AI
    clean_prompt = urllib.parse.quote(prompt.strip())
    
    # 100% Prompt-Matched AI Image Generation Engine (Pollinations)
    image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width={w}&height={h}&nologo=true&seed=42"
    fallback_image = f"https://picsum.photos/{w}/{h}"

    return {
        "prompt": prompt,
        "image_url": image_url,
        "fallback_image": fallback_image,
        "status": "success"
    }
