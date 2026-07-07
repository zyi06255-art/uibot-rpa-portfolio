"""
方案：OpenCV 去红章 + DBNet 检测 + CRNN 识别
对比 Tesseract，评测 PaddleOCR 准确度
"""
import os, sys, time, json, re
import numpy as np
from PIL import Image
import fitz
import cv2

PDF_PATH = r"C:\Users\DELL\Desktop\5.1-10.pdf"
OUTDIR = r"d:\laiye project\测试识别\ocr_results"
os.makedirs(OUTDIR, exist_ok=True)

# ============================================================
# 1. OpenCV 预处理：去红章、增强对比度
# ============================================================
def remove_red_stamp(img_bgr):
    """
    去除红色印章：利用HSV颜色空间分离红色，将其替换为背景色。
    红色印章在 OCR 中是主要噪声源，去除后识别率大幅提升。
    """
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    # 红色在 HSV 中有两个区间（0-10 和 170-180）
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 | mask2

    # 膨胀一下，覆盖印章边缘
    kernel = np.ones((3, 3), np.uint8)
    red_mask = cv2.dilate(red_mask, kernel, iterations=2)

    # 用周围区域的颜色填充红色区域（inpaint）
    img_no_stamp = cv2.inpaint(img_bgr, red_mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)

    return img_no_stamp, red_mask

def preprocess_for_ocr(img_bgr):
    """
    综合预处理流水线：
    1. 去除红色印章
    2. 转灰度 + CLAHE 增强对比度
    3. 轻微降噪
    返回处理后的 BGR 图像
    """
    # Step 1: 去红章
    img_clean, red_mask = remove_red_stamp(img_bgr)

    # Step 2: CLAHE 增强
    gray = cv2.cvtColor(img_clean, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Step 3: 轻微降噪（保边缘）
    denoised = cv2.bilateralFilter(enhanced, d=9, sigmaColor=75, sigmaSpace=75)

    # 转回 BGR 给 PaddleOCR
    result = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)

    return result, red_mask

# ============================================================
# 2. 提取 PDF 页面并用 OpenCV 预处理
# ============================================================
print("=" * 60)
print("STEP 1: OpenCV 预处理 — 去红章 + CLAHE + 降噪")
print("=" * 60)

doc = fitz.open(PDF_PATH)
N = doc.page_count

# 选代表性页面：前3页 + 采样
EVAL_PAGES = list(range(min(5, N))) + [9, 19, 29, 39, 49]
EVAL_PAGES = sorted(set(i for i in EVAL_PAGES if i < N))
print(f"评测页面: {[p+1 for p in EVAL_PAGES]} (共{len(EVAL_PAGES)}页)")

page_data = {}
for i in EVAL_PAGES:
    page = doc[i]
    mat = page.get_pixmap(dpi=300)  # 300 DPI for best quality
    img_pil = Image.frombytes("RGB", [mat.width, mat.height], mat.samples)
    img_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    # OpenCV 预处理
    img_clean, red_mask = preprocess_for_ocr(img_bgr)

    page_data[i] = {
        "raw": img_bgr,
        "clean": img_clean,
        "red_mask": red_mask,
        "size": img_bgr.shape[:2],
    }

    # 保存对比图
    cv2.imwrite(os.path.join(OUTDIR, f"p{i+1:02d}_raw.png"), img_bgr)
    cv2.imwrite(os.path.join(OUTDIR, f"p{i+1:02d}_clean.png"), img_clean)
    cv2.imwrite(os.path.join(OUTDIR, f"p{i+1:02d}_red_mask.png"), red_mask)

    # 红章占比
    red_ratio = np.sum(red_mask > 0) / (img_bgr.shape[0] * img_bgr.shape[1]) * 100
    print(f"  页{i+1}: 红章覆盖={red_ratio:.2f}%, 预处理完成")

doc.close()
print(f"\n预处理完成，对比图已保存")

# ============================================================
# 3. PaddleOCR: DBNet 检测 + CRNN 识别
# ============================================================
print("\n" + "=" * 60)
print("STEP 2: PaddleOCR (DBNet + CRNN) 识别")
print("=" * 60)

from paddleocr import PaddleOCR

# 初始化：DBNet 检测 + CRNN (ch_PP-OCRv4) 识别
# PaddleOCR 默认就是 DBNet + CRNN，显式指定
print("  初始化 PaddleOCR (DBNet det + CRNN rec)...")
t0 = time.time()
ocr_crnn = PaddleOCR(
    lang="ch",
    text_detection_model_dir=None,   # 默认 DBNet
    text_recognition_model_dir=None, # 默认 CRNN (PP-OCRv4)
    use_textline_orientation=True,   # 文字方向分类
)
print(f"  初始化完成，耗时 {time.time()-t0:.1f}s")

crnn_results = {}
crnn_times = []

for i in EVAL_PAGES:
    # 直接用 numpy 数组，避免中文路径编码问题
    img_np = page_data[i]["clean"]  # BGR numpy array

    t0 = time.time()
    result = ocr_crnn.predict(img_np)
    elapsed = time.time() - t0
    crnn_times.append(elapsed)

    # predict() returns list of PaddleResult objects
    if result and len(result) > 0:
        res = result[0]
        texts = res.get("rec_texts", []) if isinstance(res, dict) else getattr(res, "rec_texts", [])
        scores = res.get("rec_scores", []) if isinstance(res, dict) else getattr(res, "rec_scores", [])

        full_text = "\n".join(texts)
        avg_conf = np.mean(scores) * 100 if scores else 0
    else:
        texts, full_text, avg_conf = [], "", 0.0

    crnn_results[i] = {
        "text": full_text,
        "blocks": len(texts) if texts else 0,
        "avg_conf": round(avg_conf, 1),
        "time_s": round(elapsed, 2),
        "text_list": texts if texts else [],
    }

    print(f"  页{i+1}: {len(texts) if texts else 0} 文本块, "
          f"avg_conf={avg_conf:.1f}%, time={elapsed:.1f}s")

# ============================================================
# 4. 同时跑原始图片（不去红章），对比效果
# ============================================================
print("\n" + "=" * 60)
print("STEP 3: 对比 — 原始图片(不去章) PaddleOCR 识别")
print("=" * 60)

raw_results = {}
for i in EVAL_PAGES[:3]:  # 前3页做对比
    img_np = page_data[i]["raw"]  # 直接用 numpy 数组

    t0 = time.time()
    result = ocr_crnn.predict(img_np)
    elapsed = time.time() - t0

    if result and len(result) > 0:
        res = result[0]
        texts_raw = res.get("rec_texts", []) if isinstance(res, dict) else getattr(res, "rec_texts", [])
        scores_raw = res.get("rec_scores", []) if isinstance(res, dict) else getattr(res, "rec_scores", [])
        texts = list(zip(texts_raw, scores_raw))
        avg_conf = np.mean(scores_raw) * 100 if scores_raw else 0
    else:
        texts, avg_conf = [], 0.0

    raw_results[i] = {
        "blocks": len(texts),
        "avg_conf": round(avg_conf, 1),
        "time_s": round(elapsed, 2),
    }

    clean_blocks = crnn_results[i]["blocks"]
    clean_conf = crnn_results[i]["avg_conf"]
    print(f"  页{i+1}: 原始={len(texts)}块 conf={avg_conf:.1f}%  |  "
          f"去章后={clean_blocks}块 conf={clean_conf:.1f}%  |  "
          f"提升={clean_blocks - len(texts):+d}块, {clean_conf - avg_conf:+.1f}%")

# ============================================================
# 5. 保存结果 & 打印效果
# ============================================================
print("\n" + "=" * 60)
print("STEP 4: 保存识别结果")
print("=" * 60)

# 保存完整文本
paddle_text_path = os.path.join(OUTDIR, "paddleocr_crnn_output.txt")
with open(paddle_text_path, "w", encoding="utf-8") as f:
    for i in EVAL_PAGES:
        f.write(f"\n{'='*60}\n")
        f.write(f"PAGE {i+1} (PaddleOCR DBNet+CRNN, 去红章后)\n")
        f.write(f"{'='*60}\n")
        f.write(f"文本块: {crnn_results[i]['blocks']}, 平均置信度: {crnn_results[i]['avg_conf']}%\n\n")
        f.write(crnn_results[i]["text"])
        f.write("\n")

print(f"PaddleOCR 结果: {paddle_text_path}")

# ============================================================
# 6. 对比摘要
# ============================================================
print("\n" + "=" * 60)
print("SUMMARY: Tesseract vs PaddleOCR (DBNet+CRNN)")
print("=" * 60)

# 读取之前的 Tesseract 结果
tess_path = os.path.join(OUTDIR, "tesseract_full_output.txt")
if os.path.exists(tess_path):
    with open(tess_path, "r", encoding="utf-8") as f:
        tess_text = f.read()
else:
    tess_text = ""

# 统计数据
p_blocks = [crnn_results[i]["blocks"] for i in EVAL_PAGES]
p_confs = [crnn_results[i]["avg_conf"] for i in EVAL_PAGES]
p_times = crnn_times

print(f"""
{'指标':<25} {'Tesseract':>15} {'PaddleOCR(CRNN)':>20}
{'-'*60}
{'模型':<25} {'LSTM (传统)':>15} {'DBNet + CRNN':>20}
{'平均文本块/页':<25} {'~130 words':>15} {f'{np.mean(p_blocks):.0f} 块':>20}
{'平均置信度':<25} {'64.2%':>15} {f'{np.mean(p_confs):.1f}%':>20}
{'平均耗时/页':<25} {'2.4s':>15} {f'{np.mean(p_times):.1f}s':>20}
{'红章处理':<25} {'无':>15} {'HSV分离+Inpaint':>20}
{'中文字符识别':<25} {'chi_sim 引擎':>15} {'PP-OCRv4 CRNN':>20}
""")

# 去章前后对比
if raw_results:
    raw_conf_avg = np.mean([r["avg_conf"] for r in raw_results.values()])
    clean_conf_avg = np.mean([crnn_results[i]["avg_conf"] for i in raw_results.keys()])
    print(f"  去红章效果: 置信度 {raw_conf_avg:.1f}% → {clean_conf_avg:.1f}% (+{clean_conf_avg-raw_conf_avg:.1f}%)")

# 保存JSON
summary = {
    "model": "PaddleOCR DBNet + CRNN (PP-OCRv4)",
    "preprocessing": "OpenCV HSV红章分离 + Inpaint + CLAHE + Bilateral降噪",
    "pages_evaluated": len(EVAL_PAGES),
    "avg_blocks_per_page": round(np.mean(p_blocks), 1),
    "avg_confidence": round(np.mean(p_confs), 1),
    "avg_time_per_page_s": round(np.mean(p_times), 2),
    "total_time_s": round(sum(p_times), 1),
    "red_stamp_removal": {
        "avg_confidence_before": round(raw_conf_avg, 1) if raw_results else None,
        "avg_confidence_after": round(clean_conf_avg, 1) if raw_results else None,
        "improvement": round(clean_conf_avg - raw_conf_avg, 1) if raw_results else None,
    },
    "per_page": {str(k): {
        "blocks": v["blocks"],
        "avg_conf": v["avg_conf"],
        "time_s": v["time_s"],
    } for k, v in crnn_results.items()},
}
with open(os.path.join(OUTDIR, "paddle_summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"\nSummary: {os.path.join(OUTDIR, 'paddle_summary.json')}")
print("DONE!")
