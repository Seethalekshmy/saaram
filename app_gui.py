"""
SAARAM — Sign Language & Emotion Recognition
Modern CustomTkinter GUI for Mini Project Submission
"""
import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
from collections import deque
import threading
import traceback
import customtkinter as ctk
from PIL import Image, ImageTk

# ─── Local Modules ───
try:
    from nlp_module import nlp_process
    from emotion_tts import speak
except ImportError:
    print("Warning: nlp_module or emotion_tts not found.")
    nlp_process = lambda x: x
    speak = lambda x, y: print(f"SPEAK: {x} ({y})")

try:
    from ml_translator import translate_to_malayalam, speak_malayalam
except ImportError:
    print("Warning: ml_translator not found.")
    translate_to_malayalam = lambda x: ""
    speak_malayalam = lambda x: None

from emotion_detector import EmotionDetector

# ─── CONFIG ───
MODEL_PATH = "cnn26_model.h5"
LABELS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
IMG_SIZE = 400
INPUT_SIZE = 400
OFFSET = 15

# ─── Theme ───
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT       = "#7c3aed"
ACCENT_HOVER = "#6d28d9"
CYAN_ACC     = "#06b6d4"
MAGENTA_ACC  = "#ec4899"
GREEN_ACC    = "#10b981"
RED_ACC      = "#ef4444"
YELLOW_ACC   = "#f59e0b"
SURFACE      = "#1e1e2e"
SURFACE2     = "#252540"
SURFACE3     = "#2a2a4a"
TEXT_DIM     = "#8888aa"

EMOTION_COLORS = {
    "Happy":    "#fbbf24", "Sad":     "#60a5fa",
    "Angry":    "#f87171", "Neutral": "#a1a1aa",
    "Fear":     "#c084fc", "Surprise":"#fb923c",
    "Disgust":  "#4ade80",
}
EMOTION_EMOJI = {
    "Happy":"😊", "Sad":"😢", "Angry":"😠", "Neutral":"😐",
    "Fear":"😨", "Surprise":"😲", "Disgust":"🤢",
}

# ─── MediaPipe ───
try:
    import mediapipe.python.solutions as mp_solutions
    mp_hands = mp_solutions.hands
except ImportError:
    mp_hands = mp.solutions.hands

hands_detector = mp_hands.Hands(
    static_image_mode=False, max_num_hands=1,
    min_detection_confidence=0.5, min_tracking_confidence=0.5)
hands_detector_crop = mp_hands.Hands(
    static_image_mode=False, max_num_hands=1,
    min_detection_confidence=0.5, min_tracking_confidence=0.5)


def get_bbox(landmarks, img_w, img_h):
    x_min, y_min = img_w, img_h
    x_max, y_max = 0, 0
    for lm in landmarks:
        x, y = int(lm.x * img_w), int(lm.y * img_h)
        if x < x_min: x_min = x
        if x > x_max: x_max = x
        if y < y_min: y_min = y
        if y > y_max: y_max = y
    return x_min, y_min, x_max - x_min, y_max - y_min


# ═══════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════
class SaaramApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SAARAM — Sign Language & Emotion Recognition")
        self.geometry("1360x780")
        self.minsize(1200, 700)
        self.configure(fg_color="#0f0f1a")

        # State
        self.sentence = ""
        self.ml_sentence = ""
        self.last_letter = ""
        self.symbol = ""
        self.emotion = "Neutral"
        self.face_bbox = None
        self.pred_queue = deque(maxlen=15)
        self.running = True
        self.speaking = False
        self.speaking_ml = False
        self.skeleton_photo = None
        self.cam_photo = None

        self._load_models()
        self._build_ui()

        self.cap = cv2.VideoCapture(0)
        self._update_frame()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─── Models ───
    def _load_models(self):
        try:
            self.model = tf.keras.models.load_model(MODEL_PATH)
            print(f"Sign model loaded: {MODEL_PATH}")
        except Exception as e:
            print(f"Error: {e}")
            self.model = None
        self.emotion_detector = EmotionDetector(model_path="emotion_model.h5", skip_frames=3)

    # ─── UI ───
    def _build_ui(self):
        # ── TITLE BAR ──
        title_bar = ctk.CTkFrame(self, fg_color=ACCENT, corner_radius=0, height=52)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        ctk.CTkLabel(
            title_bar, text="🤟  SAARAM",
            font=ctk.CTkFont("Segoe UI", 22, "bold"), text_color="white"
        ).pack(side="left", padx=20)

        ctk.CTkLabel(
            title_bar, text="Sign Language & Emotion Recognition System",
            font=ctk.CTkFont("Segoe UI", 13), text_color="#ddd0ff"
        ).pack(side="left", padx=8)

        self.live_label = ctk.CTkLabel(
            title_bar, text="● LIVE",
            font=ctk.CTkFont("Segoe UI", 12, "bold"), text_color=GREEN_ACC
        )
        self.live_label.pack(side="right", padx=20)

        # ── BODY ──
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=14, pady=(10, 14))

        # LEFT: Camera
        left = ctk.CTkFrame(body, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        # Camera header row
        cam_hdr = ctk.CTkFrame(left, fg_color="transparent", height=28)
        cam_hdr.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(cam_hdr, text="📷  Camera Feed",
                     font=ctk.CTkFont("Segoe UI", 14, "bold"),
                     text_color="#e2e8f0").pack(side="left")

        # Legend
        legend = ctk.CTkFrame(cam_hdr, fg_color="transparent")
        legend.pack(side="right")
        ctk.CTkLabel(legend, text="■ Hand", text_color=MAGENTA_ACC,
                     font=ctk.CTkFont("Segoe UI", 11)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(legend, text="■ Face", text_color=CYAN_ACC,
                     font=ctk.CTkFont("Segoe UI", 11)).pack(side="left")

        # Camera frame
        cam_card = ctk.CTkFrame(left, fg_color=SURFACE, corner_radius=12,
                                border_width=1, border_color=SURFACE3)
        cam_card.pack(fill="both", expand=True)

        self.cam_label = ctk.CTkLabel(cam_card, text="", fg_color=SURFACE)
        self.cam_label.pack(fill="both", expand=True, padx=4, pady=4)

        # RIGHT: Panels
        right = ctk.CTkFrame(body, fg_color="transparent", width=370)
        right.pack(side="right", fill="y", padx=(14, 0))
        right.pack_propagate(False)

        # ── Detected Letter ──
        letter_card = self._card(right, "✋  Detected Letter")
        letter_card.pack(fill="x", pady=(0, 8))

        self.letter_display = ctk.CTkLabel(
            letter_card, text="—",
            font=ctk.CTkFont("Consolas", 80, "bold"),
            text_color=GREEN_ACC, height=130
        )
        self.letter_display.pack(fill="x", pady=(0, 8))

        # ── Emotion ──
        emo_card = self._card(right, "😊  Detected Emotion")
        emo_card.pack(fill="x", pady=(0, 8))

        emo_inner = ctk.CTkFrame(emo_card, fg_color="transparent")
        emo_inner.pack(fill="x", padx=16, pady=(4, 12))

        self.emo_emoji = ctk.CTkLabel(
            emo_inner, text="😐", font=ctk.CTkFont(size=42))
        self.emo_emoji.pack(side="left", padx=(0, 12))

        emo_text_frame = ctk.CTkFrame(emo_inner, fg_color="transparent")
        emo_text_frame.pack(side="left", fill="x", expand=True)

        self.emo_name = ctk.CTkLabel(
            emo_text_frame, text="Neutral",
            font=ctk.CTkFont("Segoe UI", 20, "bold"),
            text_color="#a1a1aa", anchor="w")
        self.emo_name.pack(anchor="w")

        self.emo_bar = ctk.CTkProgressBar(
            emo_text_frame, height=6, corner_radius=3,
            progress_color="#a1a1aa", fg_color=SURFACE3)
        self.emo_bar.pack(fill="x", pady=(4, 0))
        self.emo_bar.set(1.0)

        # ── Skeleton ──
        skel_card = self._card(right, "🦴  Hand Skeleton")
        skel_card.pack(fill="x", pady=(0, 8))

        skel_frame = ctk.CTkFrame(skel_card, fg_color=SURFACE3,
                                  corner_radius=8, width=160, height=160)
        skel_frame.pack(pady=(4, 10))
        skel_frame.pack_propagate(False)

        self.skeleton_label = ctk.CTkLabel(skel_frame, text="No hand", text_color=TEXT_DIM,
                                           font=ctk.CTkFont("Segoe UI", 11))
        self.skeleton_label.pack(fill="both", expand=True)

        # ── Sentence ──
        sent_card = self._card(right, "💬  Sentence Builder")
        sent_card.pack(fill="x", pady=(0, 8))

        self.sentence_display = ctk.CTkLabel(
            sent_card, text="Start signing letters…",
            font=ctk.CTkFont("Segoe UI", 15),
            text_color=TEXT_DIM, wraplength=330,
            justify="left", anchor="w"
        )
        self.sentence_display.pack(fill="x", padx=16, pady=(4, 2))
        
        self.ml_sentence_display = ctk.CTkLabel(
            sent_card, text="",
            font=ctk.CTkFont("Segoe UI", 14),
            text_color="#059669", wraplength=330,
            justify="left", anchor="w"
        )
        self.ml_sentence_display.pack(fill="x", padx=16, pady=(0, 10))

        # ── Action Buttons Row 1 ──
        btn1 = ctk.CTkFrame(right, fg_color="transparent")
        btn1.pack(fill="x", pady=(0, 6))

        self.speak_btn = ctk.CTkButton(
            btn1, text="🔊 EN Speak", font=ctk.CTkFont("Segoe UI", 12, "bold"),
            fg_color=ACCENT, hover_color=ACCENT_HOVER, corner_radius=10,
            height=40, command=self._on_speak)
        self.speak_btn.pack(side="left", fill="x", expand=True, padx=(0, 3))

        self.speak_ml_btn = ctk.CTkButton(
            btn1, text="🔊 ML Speak", font=ctk.CTkFont("Segoe UI", 12, "bold"),
            fg_color="#059669", hover_color="#047857", corner_radius=10,
            height=40, command=self._on_speak_ml)
        self.speak_ml_btn.pack(side="left", fill="x", expand=True, padx=(0, 3))

        self.nlp_btn = ctk.CTkButton(
            btn1, text="✨ NLP", font=ctk.CTkFont("Segoe UI", 12, "bold"),
            fg_color=CYAN_ACC, hover_color="#0891b2", corner_radius=10,
            text_color="#0f172a", height=40, command=self._on_nlp)
        self.nlp_btn.pack(side="left", fill="x", expand=True)

        # ── Row 2 ──
        btn2 = ctk.CTkFrame(right, fg_color="transparent")
        btn2.pack(fill="x", pady=(0, 6))

        ctk.CTkButton(
            btn2, text="␣ Space", font=ctk.CTkFont("Segoe UI", 12, "bold"),
            fg_color=SURFACE2, hover_color=SURFACE3, corner_radius=10,
            height=40, command=self._on_space
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        ctk.CTkButton(
            btn2, text="⌫ Back", font=ctk.CTkFont("Segoe UI", 12, "bold"),
            fg_color=SURFACE2, hover_color=SURFACE3, corner_radius=10,
            height=40, command=self._on_backspace
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        ctk.CTkButton(
            btn2, text="🗑 Clear", font=ctk.CTkFont("Segoe UI", 12, "bold"),
            fg_color=RED_ACC, hover_color="#dc2626", corner_radius=10,
            height=40, command=self._on_clear
        ).pack(side="left", fill="x", expand=True)

        # ── Shortcuts hint ──
        ctk.CTkLabel(
            right,
            text="ESC exit  •  S (EN)  •  M (ML)  •  C clear  •  Space gap  •  B back  •  N nlp",
            font=ctk.CTkFont("Segoe UI", 10), text_color=TEXT_DIM, wraplength=340
        ).pack(pady=(6, 0))

        # ── Key bindings ──
        self.bind("<Escape>", lambda e: self._on_close())
        self.bind("s", lambda e: self._on_speak())
        self.bind("m", lambda e: self._on_speak_ml())
        self.bind("c", lambda e: self._on_clear())
        self.bind("<space>", lambda e: self._on_space())
        self.bind("b", lambda e: self._on_backspace())
        self.bind("n", lambda e: self._on_nlp())

    # ─── Card helper ───
    def _card(self, parent, title):
        frame = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=12,
                             border_width=1, border_color=SURFACE3)
        ctk.CTkLabel(
            frame, text=title,
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=TEXT_DIM, anchor="w"
        ).pack(fill="x", padx=16, pady=(12, 4))
        return frame

    # ─── Actions ───
    def _on_speak(self):
        if not self.sentence.strip() or self.speaking:
            return
        self.speaking = True
        self.speak_btn.configure(text="🔊  Speaking…", state="disabled")

        def _t():
            try:
                final = nlp_process(self.sentence.strip())
                speak(final, self.emotion)
            except Exception as e:
                print(f"TTS Error: {e}")
            finally:
                self.speaking = False
                self.after(0, lambda: self.speak_btn.configure(
                    text="🔊 EN Speak", state="normal"))

        threading.Thread(target=_t, daemon=True).start()

    def _on_speak_ml(self):
        if not self.sentence.strip() or self.speaking_ml:
            return
        self.speaking_ml = True
        self.speak_ml_btn.configure(text="🔊  Translating…", state="disabled")

        def _m():
            try:
                # Always trigger an NLP fix before translation for best input
                final = nlp_process(self.sentence.strip())
                
                # Update UI immediately so user sees translation
                ml_txt = translate_to_malayalam(final)
                self.ml_sentence = ml_txt
                self.after(0, lambda: self.ml_sentence_display.configure(text=ml_txt))
                
                # Speak it
                self.after(0, lambda: self.speak_ml_btn.configure(text="🔊  Speaking…"))
                speak_malayalam(ml_txt)
            except Exception as e:
                print(f"ML TTS Error: {e}")
            finally:
                self.speaking_ml = False
                self.after(0, lambda: self.speak_ml_btn.configure(
                    text="🔊 ML Speak", state="normal"))

        threading.Thread(target=_m, daemon=True).start()

    def _on_clear(self):
        self.sentence = ""
        self.ml_sentence = ""
        self.last_letter = ""
        self.pred_queue.clear()
        self.sentence_display.configure(
            text="Start signing letters…", text_color=TEXT_DIM)
        self.ml_sentence_display.configure(text="")

    def _on_space(self):
        self.sentence += " "
        self.last_letter = ""
        self._update_sentence()

    def _on_backspace(self):
        if self.sentence:
            self.sentence = self.sentence[:-1]
            self.last_letter = ""
            self._update_sentence()

    def _on_nlp(self):
        if self.sentence.strip():
            try:
                self.sentence = nlp_process(self.sentence.strip())
                self._update_sentence()
            except Exception as e:
                print(f"NLP Error: {e}")

    def _update_sentence(self):
        if self.sentence:
            self.sentence_display.configure(
                text=self.sentence, text_color="#e2e8f0")
        else:
            self.sentence_display.configure(
                text="Start signing letters…", text_color=TEXT_DIM)

    # ─── Frame loop ───
    def _update_frame(self):
        if not self.running:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.after(30, self._update_frame)
            return

        frame = cv2.flip(frame, 1)
        h_f, w_f, _ = frame.shape
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # ── Emotion ──
        self.emotion, self.face_bbox = self.emotion_detector.detect(img_rgb, frame)

        if self.face_bbox:
            fx, fy, fw, fh = self.face_bbox
            cv2.rectangle(frame, (fx, fy), (fx+fw, fy+fh), (238, 211, 34), 2)
            cv2.putText(frame, self.emotion, (fx, fy-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (238, 211, 34), 2)

        ec = EMOTION_COLORS.get(self.emotion, "#a1a1aa")
        self.emo_name.configure(text=self.emotion, text_color=ec)
        self.emo_emoji.configure(text=EMOTION_EMOJI.get(self.emotion, "😐"))
        self.emo_bar.configure(progress_color=ec)

        # ── Hand ──
        results = hands_detector.process(img_rgb)
        self.symbol = ""

        if results.multi_hand_landmarks:
            hand_lms = results.multi_hand_landmarks[0]
            x, y, w, h = get_bbox(hand_lms.landmark, w_f, h_f)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (180, 114, 244), 2)

            y1 = max(0, y - OFFSET); y2 = min(h_f, y + h + OFFSET)
            x1 = max(0, x - OFFSET); x2 = min(w_f, x + w + OFFSET)
            crop = frame[y1:y2, x1:x2]

            if crop.size > 0:
                crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                hc, wc, _ = crop_rgb.shape
                res_c = hands_detector_crop.process(crop_rgb)

                if res_c.multi_hand_landmarks:
                    lms = res_c.multi_hand_landmarks[0]
                    white = np.ones((IMG_SIZE, IMG_SIZE, 3), np.uint8) * 255
                    ox = ((IMG_SIZE - w) // 2) - 15
                    oy = ((IMG_SIZE - h) // 2) - 15

                    pts = [[int(l.x*wc), int(l.y*hc)] for l in lms.landmark]

                    conns = [
                        (0,1),(1,2),(2,3),(3,4),(5,6),(6,7),(7,8),
                        (9,10),(10,11),(11,12),(13,14),(14,15),(15,16),
                        (17,18),(18,19),(19,20),(5,9),(9,13),(13,17),(0,5),(0,17)]

                    for a, b in conns:
                        if a < len(pts) and b < len(pts):
                            cv2.line(white,
                                     (pts[a][0]+ox, pts[a][1]+oy),
                                     (pts[b][0]+ox, pts[b][1]+oy),
                                     (0, 255, 0), 3)
                    for i in range(min(21, len(pts))):
                        cv2.circle(white, (pts[i][0]+ox, pts[i][1]+oy), 2, (0, 0, 255), 1)

                    # Skeleton thumbnail
                    skel_s = cv2.resize(white, (150, 150))
                    skel_rgb = cv2.cvtColor(skel_s, cv2.COLOR_BGR2RGB)
                    skel_img = Image.fromarray(skel_rgb)
                    self.skeleton_photo = ctk.CTkImage(skel_img, size=(150, 150))
                    self.skeleton_label.configure(image=self.skeleton_photo, text="")

                    # Predict
                    img_r = cv2.resize(white, (INPUT_SIZE, INPUT_SIZE))
                    pred = self.model.predict(
                        img_r.reshape(1, INPUT_SIZE, INPUT_SIZE, 3), verbose=0)
                    self.symbol = LABELS[np.argmax(pred)]

                    self.pred_queue.append(self.symbol)
                    if self.pred_queue.count(self.symbol) > 10:
                        if self.symbol != self.last_letter:
                            self.sentence += self.symbol
                            self.last_letter = self.symbol
                            self._update_sentence()

        # Letter display
        if self.symbol:
            self.letter_display.configure(text=self.symbol, text_color=GREEN_ACC)
        else:
            self.letter_display.configure(text="—", text_color=TEXT_DIM)

        # Camera display
        disp = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        lw = self.cam_label.winfo_width()
        lh = self.cam_label.winfo_height()
        if lw > 10 and lh > 10:
            sc = min(lw / w_f, lh / h_f)
            disp = cv2.resize(disp, (int(w_f * sc), int(h_f * sc)))

        pil_img = Image.fromarray(disp)
        self.cam_photo = ctk.CTkImage(pil_img, size=pil_img.size)
        self.cam_label.configure(image=self.cam_photo, text="")

        self.after(15, self._update_frame)

    # ─── Cleanup ───
    def _on_close(self):
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.emotion_detector.release()
        self.destroy()


if __name__ == "__main__":
    app = SaaramApp()
    app.mainloop()
