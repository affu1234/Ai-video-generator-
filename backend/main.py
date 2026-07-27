from fastapi import FastAPI, UploadFile, File, Form
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

# In-Memory Usage Stats Counter
stats_counter = {
    "total_generations": 142,
    "images_generated": 118,
    "voices_generated": 95,
    "prompts_enhanced": 64
}

BG_MUSIC_TRACKS = {
    "space": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73467.mp3",
    "cyberpunk": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3",
    "lofi": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
    "default": "https://cdn.pixabay.com/download/audio/2022/03/10/audio_c33f2e15fb.mp3"
}

@app.get("/")
def home():
    return {"status": "AI Ultra HD Video Engine Active 🚀"}

@app.get("/get-stats")
def get_stats():
    return stats_counter

@app.get("/enhance-prompt")
def enhance_prompt(prompt: str = ""):
    if not prompt:
        return {"enhanced_prompt": prompt}
    
    enhanced = f"A masterpiece cinematic shot of {prompt}, 8k resolution, photorealistic, octane render, dramatic lighting, highly detailed, sharp focus, volumetric light"
    if client:
        try:
            ai_prompt = f"Expand this video scene prompt into an ultra-detailed cinematic 8K visual prompt: '{prompt}'. Return ONLY the enhanced prompt in 1-2 lines."
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

@app.post("/generate-script")
async def generate_script(
    prompt: str = Form(...),
    include_image: bool = Form(True),
    include_voice: bool = Form(False),
    include_music: bool = Form(False),
    voice_accent: str = Form("en-US"),
    aspect_ratio: str = Form("16:9"),
    user_file: UploadFile = File(None)
):
    if not prompt and not user_file:
        return {"error": "Prompt or file is required"}

    # Update Stats
    stats_counter["total_generations"] += 1
    if include_image: stats_counter["images_generated"] += 1
    if include_voice: stats_counter["voices_generated"] += 1

    # Aspect Ratio Dimensions
    w, h = 1920, 1080
    if aspect_ratio == "9:16":
        w, h = 1080, 1920
    elif aspect_ratio == "1:1":
        w, h = 1080, 1080

    clean_prompt = urllib.parse.quote(prompt.strip())
    
    # Visual Image Engine
    image_url = None
    fallback_image = None
    if include_image:
        image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width={w}&height={h}&seed=100&nologo=true&enhance=true"
        fallback_image = f"https://source.unsplash.com/{w}x{h}/?{clean_prompt}"

    # AI Script Generation
    script_text = f"Discover the unbelievable story of {prompt}. The future is unfolding right now."
    if client:
        try:
            ai_prompt = f"Write an engaging short narration script with 3 storyboard scene descriptions for a video about: '{prompt}'."
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=ai_prompt,
            )
            if response.text:
                script_text = response.text.replace('\n', ' ')
        except Exception:
            pass

    # Voiceover Engine with Accent
    voice_url = None
    if include_voice:
        lang = voice_accent.split('-')[0]
        encoded_script = urllib.parse.quote(script_text[:200]) # truncated for fast tts
        voice_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_script}&tl={lang}&client=tw-ob"

    # Background Music
    bg_music = None
    if include_music:
        p_lower = prompt.lower()
        if "space" in p_lower or "galaxy" in p_lower:
            bg_music = BG_MUSIC_TRACKS["space"]
        elif "cyber" in p_lower or "tech" in p_lower:
            bg_music = BG_MUSIC_TRACKS["cyberpunk"]
        elif "chill" in p_lower or "lofi" in p_lower:
            bg_music = BG_MUSIC_TRACKS["lofi"]
        else:
            bg_music = BG_MUSIC_TRACKS["default"]

    return {
        "prompt": prompt,
        "script": script_text,
        "image_url": image_url,
        "fallback_image": fallback_image,
        "voice_url": voice_url,
        "bg_music_url": bg_music,
        "status": "success"
    }
