"""
OCR accuracy evaluation for scanned PDF using multiple engines:
- Tesseract (chi_sim + eng)
- EasyOCR
- PaddleOCR (if available)

Evaluates: confidence scores, word/char counts, processing speed
"""
import fitz  # pymupdf
import cv2
import numpy as np
from PIL import Image
import io
import time
import json
import os
import re

PDF_PATH = r"C:\Users\DELL\Desktop\5.1-10.pdf"
OUTPUT_DIR = r"d:\laiye project\测试识别\ocr_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 1. Extract pages as images
# ============================================================
print("=" * 60)
print("STEP 1: Extracting PDF pages as images...")
print("=" * 60)

doc = fitz.open(PDF_PATH)
total_pages = doc.page_count
print(f"Total pages: {total_pages}")
print(f"Page size: {doc[0].rect.width:.0f} x {doc[0].rect.height:.0f}")

# Extract first 10 pages for detailed evaluation, sample from rest
eval_pages = list(range(min(10, total_pages)))  # first 10 pages
# Also sample pages from middle and end
sample_indices = list(range(0, total_pages, max(1, total_pages // 10)))[:15]
all_eval_pages = sorted(set(eval_pages + sample_indices))
print(f"Evaluating pages: {all_eval_pages}")

page_images = {}
for i in all_eval_pages:
    page = doc[i]
    # Render at 300 DPI for good OCR quality
    mat = page.get_pixmap(dpi=300)
    img = Image.frombytes("RGB", [mat.width, mat.height], mat.samples)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    page_images[i] = {
        "pil": img,
        "cv2": img_cv,
        "size": (mat.width, mat.height)
    }
    cv2.imwrite(os.path.join(OUTPUT_DIR, f"page_{i+1:02d}.png"), img_cv)
    print(f"  Page {i+1}: {mat.width}x{mat.height}")

doc.close()

# ============================================================
# 2. Image preprocessing analysis
# ============================================================
print("\n" + "=" * 60)
print("STEP 2: Image quality analysis...")
print("=" * 60)

for i in all_eval_pages[:5]:
    img = page_images[i]["cv2"]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Laplacian variance (blur detection)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Contrast
    contrast = gray.std()

    # Estimated sharpness
    print(f"  Page {i+1}: Laplacian variance={laplacian_var:.1f} "
          f"({'Sharp' if laplacian_var > 100 else 'Blurry' if laplacian_var < 50 else 'OK'}), "
          f"Contrast std={contrast:.1f}")

# ============================================================
# 3. Tesseract OCR
# ============================================================
print("\n" + "=" * 60)
print("STEP 3: Tesseract OCR (chi_sim+eng)...")
print("=" * 60)

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

tesseract_results = {}
tesseract_times = []

for i in all_eval_pages:
    img = page_images[i]["pil"]

    t0 = time.time()
    # Try with Chinese + English
    try:
        text = pytesseract.image_to_string(img, lang="chi_sim+eng")
        data = pytesseract.image_to_data(img, lang="chi_sim+eng", output_type=pytesseract.Output.DICT)
    except:
        # Fallback to English only
        text = pytesseract.image_to_string(img, lang="eng")
        data = pytesseract.image_to_data(img, lang="eng", output_type=pytesseract.Output.DICT)
    elapsed = time.time() - t0
    tesseract_times.append(elapsed)

    # Calculate confidence stats
    confidences = [int(c) for c in data["conf"] if c != "-1"]
    avg_conf = np.mean(confidences) if confidences else 0

    # Count words with decent confidence
    words = [w for w, c in zip(data["text"], data["conf"]) if w.strip() and c != "-1" and int(c) > 30]

    tesseract_results[i] = {
        "text": text.strip(),
        "avg_confidence": round(avg_conf, 1),
        "word_count": len(words),
        "char_count": len(text.strip()),
        "time_seconds": round(elapsed, 2)
    }

    print(f"  Page {i+1}: {len(words)} words, {len(text.strip())} chars, "
          f"avg_conf={avg_conf:.1f}%, time={elapsed:.2f}s")

# ============================================================
# 4. EasyOCR
# ============================================================
print("\n" + "=" * 60)
print("STEP 4: EasyOCR (ch_sim + en)...")
print("=" * 60)

import easyocr

# Initialize once (downloads models on first run)
print("  Initializing EasyOCR reader (this may take a while on first run)...")
t0 = time.time()
reader = easyocr.Reader(["ch_sim", "en"], gpu=True)
print(f"  EasyOCR initialized in {time.time()-t0:.1f}s")

easyocr_results = {}
easyocr_times = []

for i in all_eval_pages:
    img = page_images[i]["cv2"]

    t0 = time.time()
    results = reader.readtext(img)
    elapsed = time.time() - t0
    easyocr_times.append(elapsed)

    # results: list of (bbox, text, confidence)
    texts = [r[1] for r in results]
    confidences = [r[2] for r in results]
    avg_conf = np.mean(confidences) * 100 if confidences else 0
    full_text = "\n".join(texts)

    easyocr_results[i] = {
        "text": full_text,
        "avg_confidence": round(avg_conf, 1),
        "text_blocks": len(results),
        "char_count": len(full_text),
        "time_seconds": round(elapsed, 2)
    }

    print(f"  Page {i+1}: {len(results)} text blocks, {len(full_text)} chars, "
          f"avg_conf={avg_conf:.1f}%, time={elapsed:.2f}s")

# ============================================================
# 5. Try OpenCV-based preprocessing + Tesseract
# ============================================================
print("\n" + "=" * 60)
print("STEP 5: Preprocessed OCR (OpenCV + Tesseract)...")
print("=" * 60)

preprocessed_results = {}

for i in all_eval_pages[:5]:  # First 5 pages
    img = page_images[i]["cv2"]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Try multiple preprocessing techniques
    methods = {}

    # Method 1: Simple threshold (OTSU)
    _, thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    methods["otsu"] = thresh_otsu

    # Method 2: Adaptive threshold
    thresh_adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY, 31, 2)
    methods["adaptive"] = thresh_adaptive

    # Method 3: Denoise + sharpen
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    methods["denoise_sharpen"] = sharpened

    # Method 4: CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    clahe_img = clahe.apply(gray)
    methods["clahe"] = clahe_img

    best_text = ""
    best_words = 0
    best_method = ""

    for method_name, processed_img in methods.items():
        pil_img = Image.fromarray(processed_img)
        try:
            text = pytesseract.image_to_string(pil_img, lang="chi_sim+eng")
        except:
            text = pytesseract.image_to_string(pil_img, lang="eng")

        data = pytesseract.image_to_data(pil_img, lang="chi_sim+eng", output_type=pytesseract.Output.DICT) if True else {}
        words = [w for w, c in zip(data.get("text", []), data.get("conf", []))
                 if w.strip() and c != "-1" and int(c) > 30]

        if len(words) > best_words:
            best_words = len(words)
            best_text = text
            best_method = method_name

        # Save preprocessed image
        cv2.imwrite(os.path.join(OUTPUT_DIR, f"page_{i+1:02d}_{method_name}.png"), processed_img)

    preprocessed_results[i] = {
        "best_method": best_method,
        "text": best_text.strip(),
        "word_count": best_words,
        "char_count": len(best_text.strip())
    }

    # Compare with raw
    raw_words = tesseract_results[i]["word_count"]
    print(f"  Page {i+1}: best_preprocess={best_method}, "
          f"words={best_words} (raw={raw_words}, "
          f"diff={best_words - raw_words:+d})")

# ============================================================
# 6. Summary & Comparison
# ============================================================
print("\n" + "=" * 60)
print("SUMMARY: OCR Accuracy Comparison")
print("=" * 60)

print("\n--- Tesseract (Raw) ---")
t_avg_conf = np.mean([r["avg_confidence"] for r in tesseract_results.values()])
t_total_words = sum(r["word_count"] for r in tesseract_results.values())
t_total_chars = sum(r["char_count"] for r in tesseract_results.values())
t_avg_time = np.mean(tesseract_times)
print(f"  Avg confidence: {t_avg_conf:.1f}%")
print(f"  Total words detected: {t_total_words}")
print(f"  Total chars detected: {t_total_chars}")
print(f"  Avg time/page: {t_avg_time:.2f}s")
print(f"  Total time: {sum(tesseract_times):.1f}s")

print("\n--- EasyOCR ---")
e_avg_conf = np.mean([r["avg_confidence"] for r in easyocr_results.values()])
e_total_blocks = sum(r["text_blocks"] for r in easyocr_results.values())
e_total_chars = sum(r["char_count"] for r in easyocr_results.values())
e_avg_time = np.mean(easyocr_times)
print(f"  Avg confidence: {e_avg_conf:.1f}%")
print(f"  Total text blocks: {e_total_blocks}")
print(f"  Total chars detected: {e_total_chars}")
print(f"  Avg time/page: {e_avg_time:.2f}s")
print(f"  Total time: {sum(easyocr_times):.1f}s")

print("\n--- Preprocessed Tesseract (first 5 pages) ---")
p_best_methods = [r["best_method"] for r in preprocessed_results.values()]
p_total_words = sum(r["word_count"] for r in preprocessed_results.values())
print(f"  Best methods: {dict((m, p_best_methods.count(m)) for m in set(p_best_methods))}")
print(f"  Total words: {p_total_words}")

# ============================================================
# 7. Save detailed results
# ============================================================
print("\n" + "=" * 60)
print("STEP 7: Saving results...")
print("=" * 60)

# Save full text output from best method (EasyOCR usually better for Chinese)
best_output_path = os.path.join(OUTPUT_DIR, "best_ocr_output.txt")
with open(best_output_path, "w", encoding="utf-8") as f:
    for i in sorted(all_eval_pages):
        f.write(f"\n{'='*60}\n")
        f.write(f"PAGE {i+1}\n")
        f.write(f"{'='*60}\n")
        f.write(f"EasyOCR (blocks={easyocr_results[i]['text_blocks']}, "
                f"conf={easyocr_results[i]['avg_confidence']}%):\n")
        f.write(easyocr_results[i]["text"])
        f.write(f"\n\n--- Tesseract (words={tesseract_results[i]['word_count']}, "
                f"conf={tesseract_results[i]['avg_confidence']}%): ---\n")
        f.write(tesseract_results[i]["text"])
        f.write("\n")

# Save JSON summary
summary_path = os.path.join(OUTPUT_DIR, "ocr_summary.json")
summary = {
    "pdf_path": PDF_PATH,
    "total_pages": total_pages,
    "evaluated_pages": all_eval_pages,
    "tesseract": {
        "avg_confidence": round(t_avg_conf, 1),
        "total_words": t_total_words,
        "total_chars": t_total_chars,
        "avg_time_per_page": round(t_avg_time, 2),
    },
    "easyocr": {
        "avg_confidence": round(e_avg_conf, 1),
        "total_text_blocks": e_total_blocks,
        "total_chars": e_total_chars,
        "avg_time_per_page": round(e_avg_time, 2),
    },
    "preprocessing_improvement": {
        "best_methods": dict((m, p_best_methods.count(m)) for m in set(p_best_methods)),
        "total_words_with_best": p_total_words,
    }
}
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

# Save sample text for manual review
sample_path = os.path.join(OUTPUT_DIR, "samples_for_review.txt")
with open(sample_path, "w", encoding="utf-8") as f:
    for i in all_eval_pages[:3]:
        f.write(f"\n{'='*60}\n")
        f.write(f"SAMPLE PAGE {i+1} - EasyOCR output:\n")
        f.write(f"{'='*60}\n")
        f.write(easyocr_results[i]["text"])
        f.write("\n")

print(f"Results saved to: {OUTPUT_DIR}")
print(f"  - {best_output_path}")
print(f"  - {summary_path}")
print(f"  - {sample_path}")
print(f"  - Page images (page_*.png)")

print("\n" + "=" * 60)
print("DONE! Check the output files for detailed results.")
print("=" * 60)
