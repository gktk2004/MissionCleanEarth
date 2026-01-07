import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def verify_cleaned(before_path, cleaned_file):
    before = cv2.imread(before_path)
    cleaned = cv2.imdecode(
        np.frombuffer(cleaned_file.read(), np.uint8),
        cv2.IMREAD_COLOR
    )
    cleaned_file.seek(0)

    if before is None or cleaned is None:
        return False

    before = cv2.resize(before, (600, 600))
    cleaned = cv2.resize(cleaned, (600, 600))

    # 🔹 Convert to grayscale
    gray_before = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    gray_after = cv2.cvtColor(cleaned, cv2.COLOR_BGR2GRAY)

    # 🔹 Edge detection
    edges_before = cv2.Canny(gray_before, 100, 200)
    edges_after = cv2.Canny(gray_after, 100, 200)

    edge_before_count = cv2.countNonZero(edges_before)
    edge_after_count = cv2.countNonZero(edges_after)

    # 🔹 Edge reduction %
    edge_reduction = (edge_before_count - edge_after_count) / max(edge_before_count, 1)

    # 🔹 Structural similarity
    similarity = ssim(gray_before, gray_after)

    print("Edge reduction:", edge_reduction)
    print("SSIM similarity:", similarity)

    # 🔴 STRICT CONDITIONS
    if edge_reduction < 0.40:
        return False  # Not enough trash removed

    if similarity > 0.85:
        return False  # Image too similar → not cleaned

    return True
