import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
from collections import deque
import traceback

# Import local modules if they exist
try:
    from nlp_module import nlp_process
    from emotion_tts import speak
except ImportError:
    print("Warning: nlp_module or emotion_tts not found. Disabling NLP/TTS.")
    nlp_process = lambda x: x
    speak = lambda x, y: print(f"SPEAK: {x} ({y})")

# ---------------- CONFIG ----------------
# ---------------- CONFIG ----------------
MODEL_PATH = "cnn26_model.h5"
labels = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
IMG_SIZE = 400
INPUT_SIZE = 128
OFFSET = 15

ISL_WORDS = {
    'A': 'Hello',
    'B': 'Thank you',
    'C': 'Yes',
    'D': 'No',
    'E': 'Please',
    'F': 'Help',
    'G': 'Water',
    'H': 'Food'
}

# ---------------- MEDIAPIPE SETUP ----------------
try:
    import mediapipe.python.solutions as mp_solutions
    mp_hands = mp_solutions.hands
    mp_drawing = mp_solutions.drawing_utils
except ImportError:
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

hands_detector = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

hands_detector_crop = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ---------------- HELPER ----------------
def get_bbox(landmarks, img_w, img_h):
    x_min, y_min = img_w, img_h
    x_max, y_max = 0, 0
    for lm in landmarks:
        x, y = int(lm.x * img_w), int(lm.y * img_h)
        if x < x_min: x_min = x
        if x > x_max: x_max = x
        if y < y_min: y_min = y
        if y > y_max: y_max = y
    w = x_max - x_min
    h = y_max - y_min
    return x_min, y_min, w, h
    
# ---------------- LOAD MODEL ----------------
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded.")
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# ---------------- INITIALIZE ----------------
print("Initializing camera with CAP_DSHOW...", flush=True)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("Error: Camera could not be opened.", flush=True)
    exit()

pred_queue = deque(maxlen=15)
sentence = ""
last_word = ""
emotion = "Neutral"

print("Starting loop...", flush=True)
while True:
    try:
        ret, frame = cap.read()
        if not ret:
            print("Camera error: Could not read frame", flush=True)
            break
            
        frame = cv2.flip(frame, 1)
        h_frame, w_frame, _ = frame.shape
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 1. Detect Hand in Frame
        results = hands_detector.process(img_rgb)
        
        symbol = ""
        
        if results.multi_hand_landmarks:
            hand_lms = results.multi_hand_landmarks[0]
            x, y, w, h = get_bbox(hand_lms.landmark, w_frame, h_frame)
            
            # Draw bbox on frame
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 255), 2)
            
            # 2. Crop
            # Ensure crop is within bounds
            y1, y2 = max(0, y - OFFSET), min(h_frame, y + h + OFFSET)
            x1, x2 = max(0, x - OFFSET), min(w_frame, x + w + OFFSET)
            
            img_crop = frame[y1:y2, x1:x2]
            
            if img_crop.size > 0:
                img_crop_rgb = cv2.cvtColor(img_crop, cv2.COLOR_BGR2RGB)
                h_crop, w_crop, _ = img_crop.shape
                
                # 3. Detect in Crop
                results_crop = hands_detector_crop.process(img_crop_rgb)
                
                if results_crop.multi_hand_landmarks:
                    hand_lms_crop = results_crop.multi_hand_landmarks[0]
                    
                    # 4. Prepare White Skeleton Image
                    white = np.ones((IMG_SIZE, IMG_SIZE, 3), np.uint8) * 255
                    
                    # Centering logic from training
                    # using 'w' and 'h' from original bbox for centering calculation
                    os_x = ((IMG_SIZE - w) // 2) - 15
                    os_y = ((IMG_SIZE - h) // 2) - 15
                    
                    # Map landmarks to pixel coords in crop
                    pts = []
                    for lm in hand_lms_crop.landmark:
                        px, py = int(lm.x * w_crop), int(lm.y * h_crop)
                        pts.append([px, py])
                    
                    # Draw Lines (Custom connections)
                    custom_connections = [
                        (0, 1), (1, 2), (2, 3), (3, 4),
                        (5, 6), (6, 7), (7, 8),
                        (9, 10), (10, 11), (11, 12),
                        (13, 14), (14, 15), (15, 16),
                        (17, 18), (18, 19), (19, 20),
                        (5, 9), (9, 13), (13, 17),
                        (0, 5), (0, 17)
                    ]
                    
                    for p1, p2 in custom_connections:
                        if p1 < len(pts) and p2 < len(pts):
                            x1_l, y1_l = pts[p1][0] + os_x, pts[p1][1] + os_y
                            x2_l, y2_l = pts[p2][0] + os_x, pts[p2][1] + os_y
                            cv2.line(white, (x1_l, y1_l), (x2_l, y2_l), (0, 255, 0), 3)
                        
                    for i in range(21):
                        if i < len(pts):
                            cx, cy = pts[i][0] + os_x, pts[i][1] + os_y
                            cv2.circle(white, (cx, cy), 2, (0, 0, 255), 1)
                        
                    # Show skeleton
                    cv2.imshow("Skeleton", white)
                    
                    # 5. Predict
                    img_final = white.reshape(1, IMG_SIZE, IMG_SIZE, 3)
                    pred = model.predict(img_final, verbose=0)
                    idx = np.argmax(pred)
                    symbol = labels[idx]
                    
                    # 6. Logic
                    pred_queue.append(symbol)
                    if pred_queue.count(symbol) > 10:
                        word = ISL_WORDS.get(symbol, symbol)
                        if word != last_word:
                            sentence += word + " "
                            last_word = word
                            
        # Display Info
        cv2.putText(frame, f"Symbol: {symbol}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Sentence: {sentence}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, f"Emotion: {emotion}", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.imshow("Frame", frame)
        
        # Key Handling
        key = cv2.waitKey(1) & 0xFF
        if key == 27: # ESC
            break
        elif key == ord('c'):
            sentence = ""
            last_word = ""
        elif key == ord('s'):
            try:
                final_text = nlp_process(sentence)
                speak(final_text, emotion)
            except Exception as e:
                print(f"TTS Error: {e}")
        # Emotion keys
        elif key == ord('0'): emotion = "Neutral"
        elif key == ord('1'): emotion = "Happy"
        elif key == ord('2'): emotion = "Sad"
        elif key == ord('3'): emotion = "Angry"
        
    except Exception:
        traceback.print_exc()
        break
        
cap.release()
cv2.destroyAllWindows()
