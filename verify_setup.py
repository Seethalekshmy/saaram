import sys

print(f"Python: {sys.version}")

try:
    import tensorflow
    print("TensorFlow imported")
except ImportError as e:
    print(f"TensorFlow failed: {e}")

try:
    import cvzone
    print("cvzone imported")
except ImportError as e:
    print(f"cvzone failed: {e}")

try:
    import mediapipe
    print("mediapipe imported")
except ImportError as e:
    print(f"mediapipe failed: {e}")

try:
    import cv2
    print("cv2 imported")
except ImportError as e:
    print(f"cv2 failed: {e}")

try:
    import pyttsx3
    print("pyttsx3 imported")
except ImportError as e:
    print(f"pyttsx3 failed: {e}")

try:
    import textblob
    print("textblob imported")
except ImportError as e:
    print(f"textblob failed: {e}")
