"""
Robust OCR evaluation for scanned PDF — Tesseract + preprocessing analysis
Compares: raw Tesseract vs preprocessed Tesseract
"""
import os, sys, time, json, re
import numpy as np
from PIL import Image
import fitz

PDF_PATH = r"C:\Users\DELL\Desktop\5.1-10.pdf"
OUTDIR = r"d:\laiye project\测试识别\ocr_results"
os.makedirs(OUTDIR, exist_ok=True)

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ============================
# Extract & save page images
# ============================
print("=" * 60)
print("PHASE 1: Extracting PDF pages")
print("=" * 60)

doc = fitz.open(PDF_PATH)
N = doc.page_count
print(f"Total pages: {N}")

# Evaluate: all pages for tesseract, sample for preprocessing comparison
ALL_PAGES = list(range(N))
SAMPLE_PAGES = [0, 1, 2, 9, 19, 29, 39, 49]  # first 3 + sampled across doc
SAMPLE_PAGES = [i for i in SAMPLE_PAGES if i < N]

# Extract all pages at lower DPI for speed, sample at high DPI for quality
page_paths = {}
for i in ALL_PAGES:
    page = doc[i]
    mat = page.get_pixmap(dpi=200)  # 200 DPI - good balance
    img = Image.frombytes("RGB", [mat.width, mat.height], mat.samples)
    fpath = os.path.join(OUTDIR, f"page_{i+1:03d}.png")
    img.save(fpath)
    page_paths[i] = fpath

doc.close()
print(f"Extracted {len(page_paths)} pages to {OUTDIR}")

# ============================
# PHASE 2: TESSERACT RAW
# ============================
print("\n" + "=" * 60)
print("PHASE 2: Tesseract OCR (chi_sim+eng) — ALL pages")
print("=" * 60)

tess_data = {}  # page_index -> stats
all_full_text = []

for i in ALL_PAGES:
    img = Image.open(page_paths[i])
    t0 = time.time()
    try:
        text = pytesseract.image_to_string(img, lang="chi_sim+eng")
        data = pytesseract.image_to_data(img, lang="chi_sim+eng", output_type=pytesseract.Output.DICT)
    except Exception as e:
        print(f"  Page {i+1}: chi_sim failed ({e}), trying eng...")
        text = pytesseract.image_to_string(img, lang="eng")
        data = pytesseract.image_to_data(img, lang="eng", output_type=pytesseract.Output.DICT)
    elapsed = time.time() - t0

    confs = [int(c) for c in data["conf"] if c != "-1"]
    avg_conf = float(np.mean(confs)) if confs else 0.0
    words_ok = [w.strip() for w, c in zip(data["text"], data["conf"])
                if w.strip() and c != "-1" and int(c) > 30]

    tess_data[i] = {
        "words": len(words_ok),
        "chars": len(text.strip()),
        "avg_conf": round(avg_conf, 1),
        "time_s": round(elapsed, 2),
        "text": text.strip(),
    }
    all_full_text.append(f"=== PAGE {i+1} ===\n{text.strip()}")

    if (i+1) % 10 == 0 or i < 3 or i >= N-1:
        print(f"  Page {i+1}/{N}: {len(words_ok)} words, {len(text.strip())} chars, "
              f"conf={avg_conf:.1f}%, {elapsed:.1f}s")

# Save full tesseract output
full_text_path = os.path.join(OUTDIR, "tesseract_full_output.txt")
with open(full_text_path, "w", encoding="utf-8") as f:
    f.write("\n\n".join(all_full_text))
print(f"\nFull Tesseract output saved to: {full_text_path}")

# ============================
# PHASE 3: PREPROCESSING COMPARISON
# ============================
print("\n" + "=" * 60)
print("PHASE 3: OpenCV Preprocessing Comparison (sample pages)")
print("=" * 60)

import cv2

# Load images via PIL -> numpy to avoid Unicode path issues
def load_cv2(path):
    pil = Image.open(path)
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

def ocr_image(img_cv, lang="chi_sim+eng"):
    """Run Tesseract on a cv2 image and return (text, word_count, avg_conf)"""
    pil = Image.fromarray(img_cv) if len(img_cv.shape) == 2 else Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY))
    try:
        text = pytesseract.image_to_string(pil, lang=lang)
        data = pytesseract.image_to_data(pil, lang=lang, output_type=pytesseract.Output.DICT)
    except:
        text = pytesseract.image_to_string(pil, lang="eng")
        data = pytesseract.image_to_data(pil, lang="eng", output_type=pytesseract.Output.DICT)
    confs = [int(c) for c in data["conf"] if c != "-1"]
    avg_conf = float(np.mean(confs)) if confs else 0.0
    words = [w.strip() for w, c in zip(data["text"], data["conf"])
             if w.strip() and c != "-1" and int(c) > 30]
    return text.strip(), len(words), avg_conf

preprocess_results = {}

for i in SAMPLE_PAGES:
    img = load_cv2(page_paths[i])
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    methods = {}
    # 1. OTSU binary thresholding
    _, otsu_bin = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    methods["OTSU"] = otsu_bin

    # 2. Adaptive Gaussian threshold
    adaptive_bin = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 31, 2)
    methods["AdaptiveGaussian"] = adaptive_bin

    # 3. CLAHE contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(gray)
    methods["CLAHE"] = clahe_img

    # 4. Denoise + Sharpen
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    methods["Denoise+Sharpen"] = sharpened

    # 5. OTSU after CLAHE
    clahe2 = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    clahe_img2 = clahe2.apply(gray)
    _, otsu_clahe = cv2.threshold(clahe_img2, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    methods["CLAHE+OTSU"] = otsu_clahe

    # 6. Gamma correction for bright images
    gamma = 1.5
    lut = np.array([((j / 255.0) ** gamma) * 255 for j in range(256)]).astype(np.uint8)
    gamma_corrected = cv2.LUT(gray, lut)
    methods["Gamma1.5"] = gamma_corrected

    # 7. Simple contrast stretch
    p2, p98 = np.percentile(gray, (2, 98))
    stretched = np.clip((gray - p2) * 255.0 / (p98 - p2), 0, 255).astype(np.uint8)
    methods["ContrastStretch"] = stretched

    # Test each method
    raw_text, raw_words, raw_conf = tess_data[i]["text"], tess_data[i]["words"], tess_data[i]["avg_conf"]

    best_words = raw_words
    best_method = "raw"
    best_text = raw_text
    best_conf = raw_conf

    print(f"\n  Page {i+1} (raw: {raw_words} words, conf={raw_conf:.1f}%):")
    for name, proc_img in methods.items():
        text, words, conf = ocr_image(proc_img)
        status = "BETTER" if words > raw_words else ("SAME" if words == raw_words else "worse")
        print(f"    {name:20s}: {words:4d} words, conf={conf:5.1f}%  [{status}]")

        if words > best_words or (words == best_words and conf > best_conf):
            best_words = words
            best_method = name
            best_text = text
            best_conf = conf

        # Save preprocessed sample
        cv2.imwrite(os.path.join(OUTDIR, f"page_{i+1:03d}_{name}.png"), proc_img)

    preprocess_results[i] = {
        "raw_words": raw_words,
        "raw_conf": raw_conf,
        "best_method": best_method,
        "best_words": best_words,
        "best_conf": best_conf,
        "improvement": best_words - raw_words,
    }
    print(f"    => Best: {best_method} ({best_words} words, +{best_words-raw_words} vs raw)")

# ============================
# PHASE 4: SUMMARY
# ============================
print("\n" + "=" * 60)
print("PHASE 4: SUMMARY")
print("=" * 60)

# Tesseract overall stats
all_confs = [d["avg_conf"] for d in tess_data.values()]
all_words = [d["words"] for d in tess_data.values()]
all_chars = [d["chars"] for d in tess_data.values()]
all_times = [d["time_s"] for d in tess_data.values()]

avg_conf = np.mean(all_confs)
median_conf = np.median(all_confs)
total_words = sum(all_words)
total_chars = sum(all_chars)
pages_with_text = sum(1 for w in all_words if w > 10)

print(f"""
TESSERACT RESULTS (chi_sim+eng, {N} pages):
  Avg confidence:  {avg_conf:.1f}%
  Median confidence: {median_conf:.1f}%
  Total words:     {total_words}
  Total chars:     {total_chars}
  Avg words/page:  {total_words/N:.0f}
  Avg chars/page:  {total_chars/N:.0f}
  Avg time/page:   {np.mean(all_times):.1f}s
  Total time:      {sum(all_times):.0f}s
  Pages >10 words: {pages_with_text}/{N}
""")

# Preprocessing summary
if preprocess_results:
    improvements = [r["improvement"] for r in preprocess_results.values()]
    best_methods = [r["best_method"] for r in preprocess_results.values()]
    method_counts = {}
    for m in best_methods:
        method_counts[m] = method_counts.get(m, 0) + 1

    print(f"PREPROCESSING IMPACT ({len(SAMPLE_PAGES)} sample pages):")
    print(f"  Avg word improvement: {np.mean(improvements):.1f}")
    print(f"  Best methods: {method_counts}")

    # Overall recommendation
    best_overall = max(method_counts, key=method_counts.get)
    print(f"  Recommended preprocessing: {best_overall}")

# Save summary JSON
summary = {
    "pdf": PDF_PATH,
    "pages": N,
    "image_size": f"{mat.width}x{mat.height}",
    "tesseract": {
        "avg_confidence": round(avg_conf, 1),
        "median_confidence": round(median_conf, 1),
        "total_words": total_words,
        "total_chars": total_chars,
        "avg_words_per_page": round(total_words / N, 1),
        "avg_chars_per_page": round(total_chars / N, 1),
        "avg_seconds_per_page": round(np.mean(all_times), 2),
        "pages_with_text": pages_with_text,
        "text_rate": round(pages_with_text / N * 100, 1),
    },
    "preprocessing": {
        "sample_pages": SAMPLE_PAGES,
        "avg_improvement_words": round(np.mean(improvements), 1) if preprocess_results else 0,
        "best_methods": method_counts,
        "recommended": best_overall if preprocess_results else "N/A",
        "per_page": {str(k): v for k, v in preprocess_results.items()},
    },
}
with open(os.path.join(OUTDIR, "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"\nSummary saved to: {os.path.join(OUTDIR, 'summary.json')}")
print("DONE!")
