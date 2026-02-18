from textblob import TextBlob

def nlp_process(text):
    blob = TextBlob(text)
    corrected = str(blob.correct())
    corrected = corrected.capitalize()
    if not corrected.endswith('.'):
        corrected += '.'
    return corrected
