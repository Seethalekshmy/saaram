"""
Malayalam Translation & Speech Module for SAARAM
Translates English text to Malayalam and plays it aloud using gTTS and pygame.
"""
import os
import time
import threading
from deep_translator import GoogleTranslator
from gtts import gTTS
import pygame

# Initialize pygame mixer for audio playback
pygame.mixer.init()

def translate_to_malayalam(text):
    """Translates english text to malayalam."""
    if not text or not text.strip():
        return ""
    try:
        translated = GoogleTranslator(source='en', target='ml').translate(text)
        return translated
    except Exception as e:
        print(f"Translation Error: {e}")
        return "പരിഭാഷ പരാജയപ്പെട്ടു (Translation Failed)"

def speak_malayalam(text_ml):
    """Speaks the malayalam text using gTTS and plays it."""
    if not text_ml or not text_ml.strip():
        return
        
    def _speak():
        try:
            tts = gTTS(text=text_ml, lang='ml', slow=False)
            filename = f"temp_ml_{int(time.time())}.mp3"
            tts.save(filename)
            
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # Wait for audio to finish playing
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            pygame.mixer.music.unload()
            
            # Cleanup temp file
            try:
                os.remove(filename)
            except:
                pass
                
        except Exception as e:
            print(f"gTTS Error: {e}")

    threading.Thread(target=_speak, daemon=True).start()

if __name__ == "__main__":
    # Test
    ml_text = translate_to_malayalam("Hello, how are you?")
    print("Malayalam:", ml_text)
    speak_malayalam(ml_text)
    time.sleep(3) # Wait for speech in test
