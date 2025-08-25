import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------
# Parameters
# ----------------------------
MEDIAN_KSIZE = 3
CANNY_LOW = 100
CANNY_HIGH = 200
DILATE_ITER = 1
DILATE_KERNEL_LEN = 3
AVG_KSIZE = 5
A = 50
B = 10

# ----------------------------
# Helper functions
# ----------------------------
def median_denoise(img_bgr, ksize=3):
    return cv2.medianBlur(img_bgr, ksize)

def detect_edges(img_bgr, low_thr=100, high_thr=200):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, low_thr, high_thr)
    return edges

def thicken_edges(edges, kernel_len=3, iterations=1):
    k_h = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
    k_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len))
    dilated = cv2.dilate(edges, k_h, iterations=iterations)
    dilated = cv2.dilate(dilated, k_v, iterations=iterations)
    return dilated

def average_blur(img_bgr, ksize=5):
    return cv2.blur(img_bgr, (ksize, ksize))

def quantize_color_basic(img_bgr, a=50, b=10):
    step = max(1, a - b)
    q = (img_bgr.astype(np.int32) // step)
    rep = q * (a + b / 2.0)
    rep = np.clip(rep, 0, 255).astype(np.uint8)
    return rep

def overlay_edges_black(img_bgr, edges):
    out = img_bgr.copy()
    mask = edges > 0
    out[mask] = [0, 0, 0]
    return out

def bgr2rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# ----------------------------
# Main
# ----------------------------
def cartoonize(image_path):
    orig_bgr = cv2.imread(image_path)
    if orig_bgr is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")
    
    # 1) Denoise
    denoised_bgr = median_denoise(orig_bgr, MEDIAN_KSIZE)

    # 2) Edges
    edges = detect_edges(denoised_bgr, CANNY_LOW, CANNY_HIGH)

    # 3) Thicken edges
    edges_thick = thicken_edges(edges, DILATE_KERNEL_LEN, DILATE_ITER)

    # 4) Smooth colors
    smoothed_bgr = average_blur(denoised_bgr, AVG_KSIZE)

    # 5) Color quantization
    quantized_bgr = quantize_color_basic(smoothed_bgr, A, B)

    # 6) Overlay edges
    cartoon_bgr = overlay_edges_black(quantized_bgr, edges_thick)

    # Show results using matplotlib (BGR→RGB for display)
    plt.figure(figsize=(14,10))
    plt.subplot(2,3,1); plt.imshow(bgr2rgb(orig_bgr)); plt.title("Original"); plt.axis('off')
    plt.subplot(2,3,2); plt.imshow(edges, cmap='gray'); plt.title("Canny Edges"); plt.axis('off')
    plt.subplot(2,3,3); plt.imshow(edges_thick, cmap='gray'); plt.title("Thickened Edges"); plt.axis('off')
    plt.subplot(2,3,4); plt.imshow(bgr2rgb(smoothed_bgr)); plt.title("Smoothed"); plt.axis('off')
    plt.subplot(2,3,5); plt.imshow(bgr2rgb(quantized_bgr)); plt.title("Quantized"); plt.axis('off')
    plt.subplot(2,3,6); plt.imshow(bgr2rgb(cartoon_bgr)); plt.title("Final Cartoon"); plt.axis('off')
    plt.show()

    # Save cartoon
    out_name = os.path.splitext(image_path)[0] + "_cartoon.png"
    cv2.imwrite(out_name, cartoon_bgr)
    print(f"Saved cartoon image: {out_name}")

# ----------------------------
# Run (change filename here)
# ----------------------------
if __name__ == "__main__":
    image_path = "your_photo.jpg"  # <= Replace with your image file
    cartoonize(image_path)
