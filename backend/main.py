from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from google import genai
import urllib.parse
import os

app = FastAPI()

# CORS Middleware for Frontend-Backend Communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# Real-time Stats Counter
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
    return {"status": "AI Studio Engine Active 🚀"}

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
    if not prompt:
        return {"enhanced_prompt": prompt}
    
    enhanced = f"A high quality cinematic shot of {prompt}, 8k resolution, photorealistic, octane render, vivid lighting, sharp focus"
    if client:
        try:
            ai_prompt = f"Expand this into an ultra-detailed 8K prompt in 1 concise line: '{prompt}'."
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
    prompt: str = Form(""),
    include_image: str = Form("true"),
    include_voice: str = Form("false"),
    include_music: str = Form("false"),
    voice_accent: str = Form("en-US"),
    aspect_ratio: str = Form("16:9"),
    user_file: UploadFile = File(None)
):
    is_img = include_image.lower() == "true"
    is_voc = include_voice.lower() == "true"
    is_mus = include_music.lower() == "true"

    stats_counter["total_generations"] += 1
    if is_img: stats_counter["images_generated"] += 1
    if is_voc: stats_counter["voices_generated"] += 1

    w, h = 1280, 720
    if aspect_ratio == "9:16":
        w, h = 720, 1280
    elif aspect_ratio == "1:1":
        w, h = 800, 800

    clean_prompt = urllib.parse.quote(prompt.strip() if prompt else "cinematic visual")
    
    image_url = None
    fallback_image = None
    if is_img:
        image_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width={w}&height={h}&seed=42&nologo=true"
        fallback_image = f"https://picsum.photos/{w}/{h}?random=1"

    script_text = f"Welcome to the story of {prompt if prompt else 'this scene'}. Discover the future with AI."
    if client and prompt:
        try:
            ai_prompt = f"Write a compelling 2-sentence voiceover script about: '{prompt}'."
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=ai_prompt,
            )
            if response.text:
                script_text = response.text.replace('\n', ' ')
        except Exception:
            pass

    voice_url = None
    if is_voc:
        lang = voice_accent.split('-')[0]
        encoded_script = urllib.parse.quote(script_text[:150])
        voice_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_script}&tl={lang}&client=tw-ob"

    bg_music = None
    if is_mus:
        p_lower = prompt.lower()
        if "space" in p_lower: bg_music = BG_MUSIC_TRACKS["space"]
        elif "cyber" in p_lower: bg_music = BG_MUSIC_TRACKS["cyberpunk"]
        elif "lofi" in p_lower: bg_music = BG_MUSIC_TRACKS["lofi"]
        else: bg_music = BG_MUSIC_TRACKS["default"]

    return {
        "prompt": prompt,
        "script": script_text,
        "image_url": image_url,
        "fallback_image": fallback_image,
        "voice_url": voice_url,
        "bg_music_url": bg_music,
        "status": "success"
    }
