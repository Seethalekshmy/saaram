import pyttsx3

def speak(text, emotion):
    engine = pyttsx3.init()

    if emotion == "Happy":
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1.0)
    elif emotion == "Sad":
        engine.setProperty('rate', 120)
        engine.setProperty('volume', 0.6)
    elif emotion == "Angry":
        engine.setProperty('rate', 200)
        engine.setProperty('volume', 1.0)
    else:
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.8)

    engine.say(text)
    engine.runAndWait()
