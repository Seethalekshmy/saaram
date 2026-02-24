"""
NLP Module for SAARAM
Corrects signed letter sequences into meaningful sentences.
Uses a priority dictionary for common corrections + pyspellchecker as fallback.
"""
from spellchecker import SpellChecker

spell = SpellChecker()

# Priority corrections: common misspellings from sign language letter-by-letter input
# These override the spell checker when a match is found
PRIORITY_CORRECTIONS = {
    # Greetings
    'helo':   'hello',
    'hllo':   'hello',
    'hell':   'hello',
    'helllo': 'hello',
    'helo':   'hello',
    'hi':     'hi',
    'hii':    'hi',
    'by':     'bye',
    'byee':   'bye',
    'gudby':  'goodbye',
    'godby':  'goodbye',
    
    # Common words
    'thnk':   'thank',
    'thnks':  'thanks',
    'thanku': 'thank you',
    'thnku':  'thank you',
    'yu':     'you',
    'yuu':    'you',
    'yr':     'your',
    'plese':  'please',
    'plz':    'please',
    'pls':    'please',
    'hlp':    'help',
    'sory':   'sorry',
    'srry':   'sorry',
    'srory':  'sorry',
    
    # Basics
    'gud':    'good',
    'gd':     'good',
    'bd':     'bad',
    'ys':     'yes',
    'yess':   'yes',
    'n':      'no',
    'noo':    'no',
    'ok':     'ok',
    'oky':    'okay',
    'okk':    'ok',
    
    # Food & drink
    'watr':   'water',
    'wter':   'water',
    'fod':    'food',
    'fd':     'food',
    'hungr':  'hungry',
    'hngry':  'hungry',
    'thrst':  'thirsty',
    'thrsty': 'thirsty',
    'eet':    'eat',
    'drnk':   'drink',
    
    # Emotions
    'hppy':   'happy',
    'hpy':    'happy',
    'hapy':   'happy',
    'sd':     'sad',
    'angr':   'angry',
    'angri':  'angry',
    
    # Pronouns & common
    'i':      'i',
    'im':     "i'm",
    'iam':    "i am",
    'u':      'you',
    'ur':     'your',
    'my':     'my',
    'me':     'me',
    'we':     'we',
    'thy':    'they',
    'thir':   'their',
    
    # Verbs
    'wnt':    'want',
    'ned':    'need',
    'lke':    'like',
    'lv':     'love',
    'luv':    'love',
    'lve':    'love',
    'gt':     'go',
    'cm':     'come',
    'slp':    'sleep',
    
    # Time/place
    'hom':    'home',
    'hme':    'home',
    'scol':   'school',
    'scool':  'school',
    'skol':   'school',
    'frnd':   'friend',
    'frend':  'friend',
    'mrnng':  'morning',
    'mrning': 'morning',
    'moring': 'morning',
    'nght':   'night',
    'nite':   'night',
    'tday':   'today',
    
    # Questions
    'hw':     'how',
    'wht':    'what',
    'whr':    'where',
    'whn':    'when',
    'wh':     'who',
    'ar':     'are',
    'r':      'are',
    'iz':     'is',
    'ws':     'was',
    'cn':     'can',
    'wl':     'will',
    'nt':     'not',
    'dnt':    "don't",
    'cnt':    "can't",
    'wnt':    "won't",
    
    # Names / misc
    'nam':    'name',
    'nme':    'name',
}

# Load extra words into spellchecker dictionary
spell.word_frequency.load_words(list(set(PRIORITY_CORRECTIONS.values())))
spell.word_frequency.load_words([
    'hi', 'hello', 'bye', 'thanks', 'thank', 'please', 'help',
    'yes', 'no', 'ok', 'okay', 'sorry', 'good', 'bad',
    'food', 'water', 'hungry', 'thirsty', 'happy', 'sad',
    'name', 'my', 'your', 'me', 'you', 'we', 'they',
    'want', 'need', 'like', 'love', 'go', 'come',
    'eat', 'drink', 'sleep', 'home', 'school', 'friend',
    'morning', 'night', 'how', 'what', 'where', 'when', 'who',
    'are', 'is', 'am', 'was', 'can', 'will', 'do', 'did',
])


def _correct_word(word):
    """Correct a single word using priority dict then spellchecker."""
    w = word.lower().strip()
    if not w:
        return ""
    
    # 1. Check priority dictionary first
    if w in PRIORITY_CORRECTIONS:
        return PRIORITY_CORRECTIONS[w]
    
    # 2. If word is already correct, keep it
    if w in spell:
        return w
    
    # 3. Use spell checker
    candidates = spell.candidates(w)
    if candidates:
        best = spell.correction(w)
        return best if best else w
    
    return w


def nlp_process(text):
    """Correct signed letter sequences into a proper sentence.
    
    Example: "HELO HOW AR YU" → "Hello how are you."
    """
    text = text.strip().lower()
    if not text:
        return ""

    words = text.split()
    corrected = [_correct_word(w) for w in words if w]

    result = " ".join(corrected)
    
    # Capitalize first letter and 'i'
    if result:
        result = result[0].upper() + result[1:]
        # Capitalize standalone 'i'
        result = result.replace(' i ', ' I ')
        result = result.replace(' i\'', ' I\'')
        if result.startswith('i '):
            result = 'I' + result[1:]
    
    # Add period
    if result and result[-1] not in '.!?':
        result += '.'

    return result
