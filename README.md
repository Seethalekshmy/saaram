<div align="center">
  <h1>🤟 SAARAM</h1>
  <h3>Sign Language & Emotion Recognition System</h3>
  <i>A Comprehensive Mini-Project Submission</i>
</div>

## 📌 Overview
SAARAM is an advanced real-time computer vision application designed to interpret **Indian Sign Language (ISL)** alphabets and simultaneously detect the user's **facial emotions**. 

By bridging the communication gap, SAARAM provides an accessibility tool that not only translates signs into spoken words but also infers the emotional context of the speaker, adjusting the Text-to-Speech (TTS) engine's tone accordingly.

## ✨ Key Features
- **🤲 Real-Time Sign Recognition**: Uses Mediapipe for robust hand tracking and a custom Convolutional Neural Network (CNN) trained on thousands of sign images to detect alphabets (A-Z).
- **😊 Emotion Detection**: Utilizes a secondary CNN trained on the FER2013 dataset to identify 7 core facial expressions (Happy, Sad, Angry, Neutral, Surprise, Disgust, Fear).
- **📝 Intelligent NLP Module**: Implements `pyspellchecker` with a priority dictionary to correct signed abbreviations (e.g., `THNK YU` → `Thank you`, `HI` → `Hi`) into grammatically correct sentences.
- **🗣️ Emotion-Aware TTS**: The system reads the generated sentences aloud using `pyttsx3`, automatically modifying the volume and speaking rate based on the detected emotion.
- **💻 Modern GUI**: A beautifully designed, dark-themed interface built using `CustomTkinter`, featuring live dual-ROI tracking, real-time hand skeleton visualization, and interactive controls.

## 🛠️ Technology Stack
- **Python**: Core programming language.
- **TensorFlow / Keras**: Used for training and deploying both the Sign Language (26 classes) and Emotion Detection (7 classes) CNN models.
- **OpenCV**: For real-time webcam video capture, frame manipulation, and image processing.
- **MediaPipe**: For high-accuracy real-time hand skeleton extraction and face bounding box detection.
- **CustomTkinter & Pillow**: For crafting the modern, responsive Graphical User Interface.
- **PySpellChecker**: For Natural Language Processing and intelligent auto-correction of signs.
- **PyTTSx3**: For offline, emotion-modulated Text-to-Speech synthesis.

## 🚀 How to Run
1. Ensure you have Python installed and activate the virtual environment:
   ```bash
   .\venv\Scripts\activate
   ```
2. Run the graphical application:
   ```bash
   python app_gui.py
   ```

## 🎮 Interacting with SAARAM
- **Sign Letters**: Hold your hand in the camera frame to spell out words (e.g., H-E-L-O). Wait a brief moment on each letter for it to register.
- **Space**: Press the `Space` button (or Spacebar on your keyboard) to add a gap between words.
- **NLP Fix**: Press the `NLP Fix` button (or `N`) to auto-correct the abbreviations into a perfect sentence.
- **Speak**: Press the `Speak` button (or `S`) to read the sentence out loud. The voice tone will match your facial expression!
- **Clear & Backspace**: Use the UI buttons or `C` / `B` to correct mistakes.

---
*Developed for Mini Project Submission. Built with precision and accessibility in mind.*
