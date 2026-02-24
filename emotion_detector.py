"""
Emotion Detector Module
Detects facial emotion from a video frame using MediaPipe Face Detection + CNN.
"""
import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp

# Setup MediaPipe Face Detection
try:
    import mediapipe.python.solutions as mp_solutions
    mp_face = mp_solutions.face_detection
except ImportError:
    mp_face = mp.solutions.face_detection


class EmotionDetector:
    """Detects faces and classifies emotion from video frames."""

    EMOTION_LABELS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
    IMG_SIZE = 48  # FER2013 standard input size

    def __init__(self, model_path="emotion_model.h5", detection_confidence=0.5, skip_frames=3):
        """
        Args:
            model_path: Path to the trained emotion classification model.
            detection_confidence: Minimum confidence for face detection.
            skip_frames: Run detection every N frames (for performance).
        """
        # Load emotion classification model
        try:
            self.model = tf.keras.models.load_model(model_path)
            print(f"Emotion model loaded from {model_path}")
            self.model_loaded = True
        except Exception as e:
            print(f"Warning: Could not load emotion model: {e}")
            print("Emotion detection will be disabled. Train with: python train/train_emotion_model.py")
            self.model_loaded = False

        # Initialize MediaPipe Face Detection
        self.face_detector = mp_face.FaceDetection(
            model_selection=0,  # 0 = short-range (< 2m), best for webcam
            min_detection_confidence=detection_confidence
        )

        self.skip_frames = skip_frames
        self.frame_count = 0

        # Cache last result for skipped frames
        self._last_emotion = "Neutral"
        self._last_bbox = None

    def detect(self, frame_rgb, frame_bgr):
        """
        Detect face and classify emotion.

        Args:
            frame_rgb: The video frame in RGB format (for MediaPipe).
            frame_bgr: The video frame in BGR format (for grayscale conversion).

        Returns:
            tuple: (emotion_label: str, face_bbox: (x, y, w, h) or None)
        """
        if not self.model_loaded:
            return "Neutral", None

        self.frame_count += 1

        # Skip frames for performance
        if self.frame_count % self.skip_frames != 0:
            return self._last_emotion, self._last_bbox

        h_frame, w_frame, _ = frame_rgb.shape
        results = self.face_detector.process(frame_rgb)

        if not results.detections:
            self._last_bbox = None
            return self._last_emotion, None

        # Use the first detected face
        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box

        # Convert relative coordinates to pixel coordinates
        x = max(0, int(bbox.xmin * w_frame))
        y = max(0, int(bbox.ymin * h_frame))
        w = int(bbox.width * w_frame)
        h = int(bbox.height * h_frame)

        # Clamp to frame bounds
        x2 = min(w_frame, x + w)
        y2 = min(h_frame, y + h)

        # Crop face region
        face_crop = frame_bgr[y:y2, x:x2]
        if face_crop.size == 0:
            return self._last_emotion, None

        # Preprocess for emotion model: grayscale, resize to 48x48, normalize
        face_gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        face_resized = cv2.resize(face_gray, (self.IMG_SIZE, self.IMG_SIZE))
        face_input = face_resized.reshape(1, self.IMG_SIZE, self.IMG_SIZE, 1) / 255.0

        # Predict emotion
        prediction = self.model.predict(face_input, verbose=0)
        emotion_idx = np.argmax(prediction)
        emotion_label = self.EMOTION_LABELS[emotion_idx]

        # Cache results
        self._last_emotion = emotion_label
        self._last_bbox = (x, y, w, h)

        return emotion_label, (x, y, w, h)

    def release(self):
        """Release MediaPipe resources."""
        self.face_detector.close()
