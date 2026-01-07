import cv2
import numpy as np
from PIL import Image

def load_image(file):
    image = Image.open(file).convert('RGB')
    image = np.array(image)
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

def is_duplicate(new_image_file, existing_image_file, threshold=0.75):
    img1 = load_image(new_image_file)
    img2 = load_image(existing_image_file)

    orb = cv2.ORB_create()

    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    if des1 is None or des2 is None:
        return False

    img1 = cv2.resize(img1, (600, 600))
    img2 = cv2.resize(img2, (600, 600))

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)

    matches = sorted(matches, key=lambda x: x.distance)

    good_matches = [m for m in matches if m.distance < 50]

    similarity = len(good_matches) / min(len(des1), len(des2))

    return similarity > threshold
