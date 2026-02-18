import tensorflow as tf
MODEL_PATH = "cnn26_model.h5"
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"Model loaded from {MODEL_PATH}")
    print(f"Expected Input Shape: {model.input_shape}")
except Exception as e:
    print(f"Error loading model: {e}")
