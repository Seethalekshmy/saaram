import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# ================= CONFIG =================
IMG_SIZE = 128
BATCH_SIZE = 16
EPOCHS = 10
DATASET_DIR = "AtoZ_3.1"   # Full alphabet dataset
MODEL_NAME = "cnn26_model.h5"
# =========================================

if not os.path.exists(DATASET_DIR):
    print(f"Error: Dataset directory '{DATASET_DIR}' not found.")
    exit()

print(f"Loading dataset from {DATASET_DIR}...")

datagen = ImageDataGenerator(
    rescale=1.0/255,
    validation_split=0.2
)

try:
    train_data = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training"
    )

    val_data = datagen.flow_from_directory(
        DATASET_DIR,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation"
    )
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

print(f"Found {train_data.num_classes} classes: {list(train_data.class_indices.keys())}")

print("Building CNN model...")

model = Sequential([
    Conv2D(32, (3, 3), activation="relu", input_shape=(IMG_SIZE, IMG_SIZE, 3)),
    MaxPooling2D(2, 2),

    Conv2D(64, (3, 3), activation="relu"),
    MaxPooling2D(2, 2),

    Flatten(),
    Dense(128, activation="relu"),
    Dropout(0.5),

    Dense(train_data.num_classes, activation="softmax")
])

model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

print("Training started...")
try:
    model.fit(
        train_data,
        validation_data=val_data,
        epochs=EPOCHS
    )
    
    model.save(MODEL_NAME)
    print(f"✅ Training complete. Model saved as {MODEL_NAME}")
except Exception as e:
    print(f"Training failed: {e}")
