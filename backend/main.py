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

# Background audio collection
BG_MUSIC_TRACKS = {
    "space": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8c8a73467.mp3",
    "cyberpunk": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3",
    "default": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3"
}

@app.get("/")
def home():
    return {"message": "AI Video Generator Backend Active 🚀"}

@app.get("/generate-script")
def generate_script(prompt: str = ""):
    if not prompt:
        return {"error": "Prompt is required"}

    # Dynamic Pollinations AI Image Engine
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=576&nologo=true"

    script_text = f"Welcome to the visual world of {prompt}. Experience the future of AI generation."

    if client:
        try:
            ai_prompt = f"Write a short 2-sentence captivating video voiceover script about: '{prompt}'."
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=ai_prompt,
            )
            script_text = response.text
        except Exception as e:
            pass

    # Dynamic Google TTS Voiceover URL
    encoded_script = urllib.parse.quote(script_text)
    voice_url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_script}&tl=en&client=tw-ob"

    # Select suitable background music
    prompt_lower = prompt.lower()
    if "space" in prompt_lower or "galaxy" in prompt_lower:
        bg_music = BG_MUSIC_TRACKS["space"]
    elif "cyber" in prompt_lower or "tech" in prompt_lower:
        bg_music = BG_MUSIC_TRACKS["cyberpunk"]
    else:
        bg_music = BG_MUSIC_TRACKS["default"]

    return {
        "prompt": prompt,
        "script": script_text,
        "image_url": image_url,
        "voice_url": voice_url,
        "bg_music_url": bg_music,
        "status": "success"
    }
