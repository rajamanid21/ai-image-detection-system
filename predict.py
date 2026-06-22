import cv2
import numpy as np
from PIL import Image



def predict_image(image_path):
    # Read image with OpenCV
    img = cv2.imread(image_path)
    if img is None:
        return {'label': 'Error', 'confidence': 0.0}

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Compute Laplacian variance (edge sharpness)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()

    # Heuristic thresholds (tuned for demo)
    threshold_low = 100
    threshold_high = 500

    if variance < threshold_low:
        label = "AI-Generated"
        confidence = max(0, min(1, (threshold_low - variance) / threshold_low))
    elif variance > threshold_high:
        label = "Real"
        confidence = max(0, min(1, (variance - threshold_high) / threshold_high))
    else:
        label = "Uncertain"
        confidence = 0.5

    confidence_percent = round(confidence * 100, 2)

    # Use PIL to get extra info
    pil_img = Image.open(image_path)
    img_format = pil_img.format
    width, height = pil_img.size

    return {
        'label': label,
        'confidence': confidence_percent,
        'variance': round(variance, 2),
        'format': img_format,
        'width': width,
        'height': height
    }