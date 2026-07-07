# ============================================================
# PDF识别.py - UiBot Python流程块
# 必须导入: os, json, copy, decimal, random + apa_runtime
# 禁止: f-string, __file__, 整体try
# ============================================================
import os, json, copy, decimal, random
from apa_runtime import *

# 必须在导入 paddle 前禁用 oneDNN
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["KMP_AFFINITY"] = "disabled"

import fitz  # pymupdf
import time

def detect_pdf_type(doc):
    """检测PDF类型: 'digital'(有嵌入文字) 或 'scanned'(扫描件)"""
    total_chars = 0
    for page_num in range(min(3, doc.page_count)):
        page = doc[page_num]
        text = page.get_text()
        total_chars = total_chars + len(text.strip())
    if total_chars >= 50:
        return "digital"
    return "scanned"

def extract_digital_pdf(doc, page_num):
    """从数字PDF按坐标提取结构化文字"""
    page = doc[page_num]
    blocks = page.get_text("blocks")

    items = []
    for b in blocks:
        x0, y0, x1, y1, text, btype, _ = b
        text = text.strip()
        if text:
            items.append({
                "x": round((x0 + x1) / 2, 0),
                "y": round((y0 + y1) / 2, 0),
                "x0": round(x0, 0),
                "y0": round(y0, 0),
                "x1": round(x1, 0),
                "y1": round(y1, 0),
                "text": text,
            })
    return items

def extract_scanned_pdf(img_bgr):
    """从扫描件图片用PaddleOCR识别"""
    try:
        from paddleocr import PaddleOCR
        import numpy as np
    except ImportError:
        Log.Error("PaddleOCR未安装，无法识别扫描件。请执行: pip install paddleocr")
        raise

    # 初始化 (每10页重建一次防止内存泄漏)
    ocr = PaddleOCR(lang="ch", use_angle_cls=False, show_log=False, use_gpu=False)

    result = ocr.ocr(img_bgr, cls=False)

    items = []
    if result and result[0]:
        for line in result[0]:
            bbox, (text, conf) = line
            xs = [p[0] for p in bbox]
            ys = [p[1] for p in bbox]
            items.append({
                "x": round(sum(xs) / len(xs), 0),
                "y": round(sum(ys) / len(ys), 0),
                "x0": round(min(xs), 0),
                "y0": round(min(ys), 0),
                "x1": round(max(xs), 0),
                "y1": round(max(ys), 0),
                "text": text,
                "conf": round(conf, 4),
            })

    # 释放
    del ocr

    return items

def clean_text(text):
    """清洗文本: 合并多余空白"""
    import re
    return re.sub(r"\s+", " ", text).strip()


# ===== 主入口 =====
def main(argument):
    start_time = time.time()

    # 1. 读取参数: argument > GlobalVariables > 默认路径
    pdf_path = argument if isinstance(argument, str) and argument else ""
    if not pdf_path:
        pdf_path = GlobalVariables.get("pdfPath", "")
    if not pdf_path:
        pdf_path = r"C:\Users\DELL\Desktop\一个电子承兑商业汇票.pdf"
    output_dir = GlobalVariables.get("outputDir", "")

    if not output_dir:
        output_dir = os.path.dirname(pdf_path)

    os.makedirs(output_dir, exist_ok=True)

    Log.Info("开始识别PDF: {}".format(pdf_path))

    # 2. 打开PDF
    doc = fitz.open(pdf_path)
    total_pages = doc.page_count
    Log.Info("PDF共 {} 页".format(total_pages))

    # 3. 检测类型
    pdf_type = detect_pdf_type(doc)
    Log.Info("检测类型: {}".format(pdf_type))

    # 4. 提取文字
    all_pages = []
    confidence_scores = []

    if pdf_type == "digital":
        # === 数字PDF ===
        for page_num in range(total_pages):
            items = extract_digital_pdf(doc, page_num)
            all_pages.append({
                "page": page_num + 1,
                "items": items,
                "count": len(items),
            })
            # 数字PDF嵌入文字准确度100%
            confidence_scores.append(100.0)

    else:
        # === 扫描件PDF ===
        import cv2
        import numpy as np
        from PIL import Image

        for page_num in range(total_pages):
            page = doc[page_num]
            mat = page.get_pixmap(dpi=200)
            img_pil = Image.frombytes("RGB", [mat.width, mat.height], mat.samples)
            img_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

            items = extract_scanned_pdf(img_bgr)

            confs = [it.get("conf", 0) for it in items]
            avg_conf = round(np.mean(confs) * 100, 1) if confs else 0

            all_pages.append({
                "page": page_num + 1,
                "items": items,
                "count": len(items),
                "avg_confidence": avg_conf,
            })
            confidence_scores.append(avg_conf)

            Log.Info("  第{}页: {}块, 置信度{}%".format(page_num + 1, len(items), avg_conf))

    doc.close()

    # 5. 构建结果
    elapsed = round(time.time() - start_time, 2)

    result = {
        "file": pdf_path,
        "type": pdf_type,
        "total_pages": total_pages,
        "avg_confidence": round(sum(confidence_scores) / len(confidence_scores), 1) if confidence_scores else 0,
        "elapsed_seconds": elapsed,
        "pages": all_pages,
    }

    # 6. 保存JSON
    json_path = os.path.join(output_dir, "result.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    Log.Info("识别完成: {} 页, 类型={}, 耗时={}s, 结果={}".format(
        total_pages, pdf_type, elapsed, json_path))

    # 7. 返回
    return {
        "type": pdf_type,
        "pages": total_pages,
        "elapsed": elapsed,
        "json_path": json_path,
    }
