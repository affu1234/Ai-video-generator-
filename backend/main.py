from fastapi import FastAPI, Form
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
    "total_generations": 210,
    "images_generated": 175,
    "voices_generated": 140,
    "prompts_enhanced": 95
}

BG_MUSIC_TRACKS = {
    "space": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73467.mp3",
    "cyberpunk": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3",
    "lofi": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
    "default": "https://cdn.pixabay.com/download/audio/2022/03/10/audio_c33f2e15fb.mp3"
}

@app.get("/")
def home():
    return {"status": "AI Engine Active 🚀"}

@app.get("/get-stats")
def get_stats():
    return {
        "total": stats_counter["total_generations"],
        "images": stats_counter["images_generated"],
        "voices": stats_counter["voices_generated"],
        "prompts": stats_counter["prompts_enhanced"]
    }

@app.get("/enhance-prompt")
def enhance_prompt(prompt: str = ""):
    if not prompt or prompt.strip() == "":
        return {"enhanced_prompt": "Cinematic high resolution realistic scene"}
    
    enhanced = f"A realistic ultra-detailed cinematic 8k shot of {prompt}, dramatic lighting, sharp focus, masterpiece"
    if client:
        try:
            ai_prompt = f"Expand this into an ultra-detailed 8K video prompt in 1 concise line: '{prompt}'."
            res = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=ai_prompt,
            )
            if res and res.text:
                enhanced = res.text.strip().replace('\n', ' ')
        except Exception:
            pass
            
    stats_counter["prompts_enhanced"] += 1
    return {"enhanced_prompt": enhanced}

@app.post("/generate-script")
async def generate_script(
    prompt: str = Form(""),
    include_image: str = Form("true"),
    include_voice: str = Form("false"),
    include_music: str = Form("false"),
    voice_accent: str = Form("en-US"),
    aspect_ratio: str = Form("16:9")
):
    is_img = str(include_image).lower() == "true"
    is_voc = str(include_voice).lower() == "true"
    is_mus = str(include_music).lower() == "true"

    stats_counter["total_generations"] += 1
    if is_img: stats_counter["images_generated"] += 1
    if is_voc: stats_counter["voices_generated"] += 1

    # Ratio Handling
    w, h = 1280, 720
    if aspect_ratio == "9:16":
        w, h = 720, 1280
    elif aspect_ratio == "1:1":
        w, h = 800, 800

    clean_text = prompt.strip() if prompt else "cinematic wallpaper"
    encoded_prompt = urllib.parse.quote(clean_text)
    
    # Dual Image URLs (Primary AI + Fallback)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={w}&height={h}&nologo=true"
    fallback_image = f"https://source.unsplash.com/featured/{w}x{h}/?{encoded_prompt}"

    # Script Generation
    script_text = f"Welcome to the world of {clean_text}. Experience the futuristic AI creation today."
    if client and prompt:
        try:
            ai_prompt = f"Write a catchy 2-sentence narration script about: '{clean_text}'."
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=ai_prompt,
            )
            if response and response.text:
                script_text = response.text.strip().replace('\n', ' ')
        except Exception:
            pass

    # Music Engine
    bg_music = None
    if is_mus:
        p_lower = clean_text.lower()
        if "space" in p_lower: bg_music = BG_MUSIC_TRACKS["space"]
        elif "cyber" in p_lower: bg_music = BG_MUSIC_TRACKS["cyberpunk"]
        elif "lofi" in p_lower: bg_music = BG_MUSIC_TRACKS["lofi"]
        else: bg_music = BG_MUSIC_TRACKS["default"]

    return {
        "prompt": clean_text,
        "script": script_text,
        "image_url": image_url,
        "fallback_image": fallback_image,
        "bg_music_url": bg_music,
        "status": "success"
    }
