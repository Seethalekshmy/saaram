"""
Emotion-Aware Text-to-Speech using ElevenLabs (Ultimate Emotion AI)
Provides impossibly realistic emotive voices based on standard voice IDs.
Falls back to Google TTS if the API limit is reached.
"""
import os
import time
import pygame
from elevenlabs.client import ElevenLabs

# Initialize pygame mixer
try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()
except:
    pass

# The user's ElevenLabs API Key
API_KEY = "sk_553051f12983328359ebc2671d64acf5735dd2c089573c67"
client = ElevenLabs(api_key=API_KEY)

# Map emotions to standard ElevenLabs Free Voice IDs to change the character/tone
VOICE_IDS = {
    "Happy":    "EXAVITQu4vr4xnSDxMaL", # Bella (Soft, bright)
    "Sad":      "21m00Tcm4TlvDq8ikWAM", # Rachel (Calm)
    "Angry":    "pNInz6obpgDQGcFmaJgB", # Adam (Deep, strong roar)
    "Neutral":  "ErXwobaYiN019PkySvjV", # Antoni (Well-rounded professional)
    "Fear":     "21m00Tcm4TlvDq8ikWAM", # Rachel
    "Surprise": "EXAVITQu4vr4xnSDxMaL", # Bella
    "Disgust":  "pNInz6obpgDQGcFmaJgB", # Adam
}

def speak(text, emotion="Neutral"):
    if not text or not text.strip():
        return

    try:
        # Select the pre-mapped emotional voice
        voice_id = VOICE_IDS.get(emotion, VOICE_IDS["Neutral"])
        
        # Call ElevenLabs API
        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        # Save streamed chunks to file
        filename = f"temp_el_{int(time.time()*1000)}.mp3"
        with open(filename, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)
                
        # Play the audio
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        # Wait for audio to finish playing (blocking)
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        pygame.mixer.music.unload()
        
        # Cleanup temp file
        try:
            os.remove(filename)
        except:
            pass
            
    except Exception as e:
        print(f"ElevenLabs TTS Error: {e}. Falling back to gTTS...")
        # Fallback to gTTS if API limit reached or network error
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='en')
            filename = f"temp_gtts_{int(time.time()*1000)}.mp3"
            tts.save(filename)
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.music.unload()
            try:
                os.remove(filename)
            except:
                pass
        except:
            pass

if __name__ == "__main__":
    print("Testing ElevenLabs integration with Happy voice...")
    speak("Hello! I am so incredibly happy to meet you today!", "Happy")
    
    print("Testing ElevenLabs integration with Angry voice...")
    speak("I told you absolutely not to touch that!", "Angry")
