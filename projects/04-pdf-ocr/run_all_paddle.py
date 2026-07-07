import os
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["KMP_AFFINITY"] = "disabled"
os.environ["OMP_NUM_THREADS"] = "1"

import cv2, numpy as np, fitz, time, json, gc
from PIL import Image

PDF_PATH = r"C:\Users\DELL\Desktop\5.1-10.pdf"
OUTDIR = r"d:\laiye project\测试识别\ocr_results"
os.makedirs(OUTDIR, exist_ok=True)

from paddleocr import PaddleOCR

def make_ocr():
    return PaddleOCR(lang="ch", use_angle_cls=False, show_log=False, use_gpu=False)

def preprocess(img_bgr):
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    m1 = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
    m2 = cv2.inRange(hsv, np.array([170, 50, 50]), np.array([180, 255, 255]))
    red_mask = m1 | m2
    kernel = np.ones((3, 3), np.uint8)
    red_mask = cv2.dilate(red_mask, kernel, iterations=2)
    clean = cv2.inpaint(img_bgr, red_mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
    gray = cv2.cvtColor(clean, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

doc = fitz.open(PDF_PATH)
N = doc.page_count
print(f"Total: {N} pages, running in batches of 10...")

all_results = []
total_time = 0
total_blocks = 0
all_confs = []

ocr = make_ocr()
batch_size = 10

for i in range(N):
    # 每10页重建OCR引擎，释放oneDNN内存
    if i > 0 and i % batch_size == 0:
        del ocr
        gc.collect()
        ocr = make_ocr()
        print(f"  [batch reset at page {i+1}]")

    page = doc[i]
    mat = page.get_pixmap(dpi=200)
    img_pil = Image.frombytes("RGB", [mat.width, mat.height], mat.samples)
    img_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    img_clean = preprocess(img_bgr)

    t0 = time.time()
    result = ocr.ocr(img_clean, cls=False)
    elapsed = time.time() - t0
    total_time += elapsed

    if result and result[0]:
        lines = result[0]
        texts = [l[1][0] for l in lines]
        scores = [l[1][1] for l in lines]
        avg_conf = np.mean(scores) * 100
        all_confs.append(avg_conf)
        total_blocks += len(texts)
        page_text = "\n".join(texts)
    else:
        texts, avg_conf, page_text = [], 0, ""

    all_results.append({
        "page": i + 1,
        "blocks": len(texts),
        "avg_conf": round(avg_conf, 1),
        "time_s": round(elapsed, 2),
        "text": page_text,
    })

    print(f"  Page {i+1}/{N}: {len(texts)} blocks, conf={avg_conf:.1f}%, {elapsed:.1f}s")

    del img_bgr, img_clean
    gc.collect()

doc.close()

# Save TXT
txt_path = os.path.join(OUTDIR, "paddleocr_full_output.txt")
with open(txt_path, "w", encoding="utf-8") as f:
    f.write(f"PaddleOCR (DBNet + CRNN) 全量识别结果\n")
    f.write(f"文件: {PDF_PATH}\n")
    f.write(f"预处理: OpenCV HSV去红章 + CLAHE增强\n")
    f.write(f"总页数: {N}\n")
    f.write(f"平均置信度: {np.mean(all_confs):.1f}%\n")
    f.write(f"总文本块: {total_blocks}\n")
    f.write(f"总耗时: {total_time:.0f}s\n")
    f.write("=" * 60 + "\n")
    for r in all_results:
        f.write(f"\n{'='*60}\n")
        f.write(f"PAGE {r['page']}  |  {r['blocks']} blocks  |  conf={r['avg_conf']}%  |  {r['time_s']}s\n")
        f.write(f"{'='*60}\n")
        f.write(r["text"])
        f.write("\n")

print(f"\nDone! TXT -> {txt_path}")
print(f"Avg conf: {np.mean(all_confs):.1f}% | Blocks: {total_blocks} | Time: {total_time:.0f}s")
