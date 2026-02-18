import cv2
import numpy as np

img = cv2.imread("test.jpg")
if img is None:
    print("Image not found")
else:
    print(f"Shape: {img.shape}")
    print(f"Mean color: {np.mean(img)}")
    # Check if mostly white
    if np.mean(img) > 200:
        print("Image is likely a skeleton image (mostly white).")
    else:
        print("Image is likely a raw photo (not mostly white).")
