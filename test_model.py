import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
import os

# ---------------- CONFIG ----------------
MODEL_PATH = "cnn8grps_rad1_model.h5"
IMG_PATH = "test.jpg"
labels = ['A','B','C','D','E','F','G','H']
OFFSET = 15
IMG_SIZE = 400

# ---------------- LOAD MODEL ----------------
if not os.path.exists(MODEL_PATH):
    print(f"ERROR: Model file {MODEL_PATH} not found.")
    exit()

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:
    print(f"ERROR: Failed to load model. {e}")
    exit()

# ---------------- MEDIAPIPE SETUP ----------------
try:
    # Explicit import of solutions if needed, or just standard
    # Some environments need: import mediapipe.python.solutions as mp_solutions
    import mediapipe.python.solutions as mp_solutions
    mp_hands = mp_solutions.hands
    mp_drawing = mp_solutions.drawing_utils
except ImportError:
    # Fallback
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

hands_detector = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
)

hands_detector_crop = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
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

# ---------------- LOAD IMAGE ----------------
img = cv2.imread(IMG_PATH)
if img is None:
    print(f"ERROR: {IMG_PATH} not found.")
    exit()

img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
h_img, w_img, _ = img.shape

# ---------------- PREPROCESS ----------------
# 1. Detect Hand in Full Image
results = hands_detector.process(img_rgb)

if not results.multi_hand_landmarks:
    print("No hands detected in image.")
    exit()

# Get first hand
hand_lms = results.multi_hand_landmarks[0]
x, y, w, h = get_bbox(hand_lms.landmark, w_img, h_img)

# 2. Crop Image
# Note: Data collection used a somewhat loose crop logic. 
# cvzone bbox is [x, y, w, h].
# We just calculated it from landmarks.
img_crop = img[y - OFFSET : y + h + OFFSET, x - OFFSET : x + w + OFFSET]

if img_crop.size == 0:
    print("ERROR: Cropped image is empty.")
    exit()

img_crop_rgb = cv2.cvtColor(img_crop, cv2.COLOR_BGR2RGB)
h_crop, w_crop, _ = img_crop.shape

# 3. Detect Hand in Crop
results_crop = hands_detector_crop.process(img_crop_rgb)

if results_crop.multi_hand_landmarks:
    hand_lms_crop = results_crop.multi_hand_landmarks[0]
    
    # 4. Prepare White Background
    white = np.ones((IMG_SIZE, IMG_SIZE, 3), np.uint8) * 255
    
    # 5. Center and Draw Skeleton
    # w and h here should be from the INITIAL, FULL-IMAGE detection to match training logic?
    # verify_setup.py used: os = ((400 - w) // 2) - 15  where w is from full frame.
    
    os_x = ((IMG_SIZE - w) // 2) - 15
    os_y = ((IMG_SIZE - h) // 2) - 15
    
    connections = mp_hands.HAND_CONNECTIONS
    # MediaPipe Hand Connections are robust.
    # But we need to draw lines and circles manually to match the visual style of training data.
    # The training data drew specific lines.
    # Let's map MP landmarks (0-20) to pixels in crop.
    
    pts = []
    for lm in hand_lms_crop.landmark:
        px, py = int(lm.x * w_crop), int(lm.y * h_crop)
        pts.append([px, py])
    
    # Draw Lines (using custom connections from training script to ensure exact match)
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
        x1, y1 = pts[p1][0] + os_x, pts[p1][1] + os_y
        x2, y2 = pts[p2][0] + os_x, pts[p2][1] + os_y
        cv2.line(white, (x1, y1), (x2, y2), (0, 255, 0), 3)

    for i in range(21):
        cx, cy = pts[i][0] + os_x, pts[i][1] + os_y
        cv2.circle(white, (cx, cy), 2, (0, 0, 255), 1)

    # 6. Predict
    img_final = white.reshape(1, 400, 400, 3)
    cv2.imwrite("debug_skeleton_mp.jpg", white)
    
    prediction = model.predict(img_final, verbose=0)
    idx = np.argmax(prediction)
    print(f"Raw Prediction: {prediction}")
    print(f"Predicted Class: {labels[idx]}")

else:
    print("Hand detected in full image but not in crop.")
