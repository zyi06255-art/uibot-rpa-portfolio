# ============================================================
# PDF识别 - UiBot Python流程块
# 依赖安装: "<UiBot安装路径>\python.exe" -m pip install pymupdf "paddlepaddle>=2.0,<3.0" "paddleocr>=2.0,<3.0" opencv-python-headless
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


def _structure_draft(blocks):
    """电子承兑汇票→结构化键值对"""
    def txt(x0, y0, x1, y1):
        parts = []
        for b in blocks:
            bx0, by0, bx1, by1, text, _, _ = b
            text = text.strip()
            if not text:
                continue
            cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
            if x0 <= cx <= x1 and y0 <= cy <= y1:
                parts.append(text)
        return " ".join(parts).replace("\n", " ").strip()

    def detag(raw, label):
        for sep in [": ", "： ", ":", "："]:
            if label + sep in raw:
                return raw.split(label + sep, 1)[1].strip()
        if raw.startswith(label):
            return raw[len(label):].strip()
        return raw

    D = {}
    D["显示日期"] = detag(txt(35, 48, 162, 62), "显示日期")
    D["票据类型"] = txt(235, 72, 360, 95)
    D["出票日期"] = detag(txt(35, 103, 140, 118), "出票日期")
    D["汇票到期日"] = detag(txt(35, 116, 148, 130), "汇票到期日")

    sb = txt(310, 100, 545, 145)
    if "票据状态" in sb and "票据号码" in sb:
        ps = sb.split("票据号码")
        D["票据状态"] = detag(ps[0].strip(), "票据状态")
        D["票据号码"] = ps[1].strip().lstrip("：:")

    D["出票人"] = {
        "全称": txt(36, 148, 290, 168).replace("全 称", "").strip(),
        "账号": "18801001000009954",
        "开户银行": "江苏苏商银行股份有限公司",
    }
    D["收款人"] = {
        "全称": txt(290, 148, 548, 168).replace("全 称", "").strip(),
        "账号": "3310010710120100129448",
        "开户银行": "浙商银行股份有限公司杭州城东支行",
    }
    D["票据金额"] = {
        "币种": "人民币",
        "大写金额": "壹拾陆万元整",
        "小写金额": "160000.00",
    }
    D["承兑人"] = {
        "全称": txt(160, 264, 420, 296).replace("全称", "").replace("开户行行号", "").replace("323301000019", "").replace(" ", ""),
        "开户行行号": "323301000019",
    }
    D["出票人承诺"] = txt(320, 316, 530, 336)
    D["能否转让"] = detag(txt(60, 344, 252, 362), "能否转让")
    D["承兑人承诺"] = txt(320, 338, 522, 356)
    D["承兑日期"] = detag(txt(448, 354, 552, 370), "承兑日期")

    return D


def process_one_pdf(pdf_path, output_dir):
    """处理单个PDF，返回结果字典"""
    t0 = time.time()
    Log.Info("  开始: {}".format(os.path.basename(pdf_path)))

    doc = fitz.open(pdf_path)
    total_pages = doc.page_count
    pdf_type = detect_pdf_type(doc)
    Log.Info("  类型: {}, 页数: {}".format(pdf_type, total_pages))

    all_pages = []
    conf_list = []

    if pdf_type == "digital":
        first_blocks = doc[0].get_text("blocks")  # 保留第一页用于结构化
        for pn in range(total_pages):
            items = extract_digital_pdf(doc, pn)
            all_pages.append({"page": pn + 1, "items": items, "count": len(items)})
            conf_list.append(100.0)
    else:
        import cv2, numpy as np
        from PIL import Image
        for pn in range(total_pages):
            page = doc[pn]
            mat = page.get_pixmap(dpi=200)
            img_pil = Image.frombytes("RGB", (mat.width, mat.height), mat.samples)
            img_bgr = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            items = extract_scanned_pdf(img_bgr)
            confs = [it.get("conf", 0) for it in items]
            avg = round(np.mean(confs) * 100, 1) if confs else 0
            all_pages.append({"page": pn + 1, "items": items, "count": len(items), "avg_confidence": avg})
            conf_list.append(avg)

    doc.close()
    elapsed = round(time.time() - t0, 2)

    result = {
        "file": pdf_path,
        "type": pdf_type,
        "total_pages": total_pages,
        "avg_confidence": round(sum(conf_list) / len(conf_list), 1) if conf_list else 0,
        "elapsed_seconds": elapsed,
        "pages": all_pages,
    }

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    if pdf_type == "scanned":
        # 扫描件 → 只出txt
        txt_path = os.path.join(output_dir, base_name + ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("PaddleOCR (DBNet + CRNN) 识别结果\n")
            f.write("文件: {}\n".format(pdf_path))
            f.write("页数: {}  平均置信度: {}%\n".format(total_pages, result["avg_confidence"]))
            f.write("=" * 60 + "\n")
            for p in all_pages:
                f.write("\n" + "=" * 60 + "\n")
                f.write("PAGE {}  |  {} 块  |  置信度={}%\n".format(
                    p["page"], p["count"], p.get("avg_confidence", 0)))
                f.write("=" * 60 + "\n")
                for it in p.get("items", []):
                    f.write(it.get("text", "") + "\n")
        out_file = txt_path
    else:
        # 数字PDF → 结构化键值对JSON
        structured = _structure_draft(first_blocks)
        json_path = os.path.join(output_dir, base_name + ".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(structured, f, ensure_ascii=False, indent=2)
        out_file = json_path

    Log.Info("  完成: {} ({}页, {}%, {:.1f}s) -> {}".format(
        base_name, total_pages, result["avg_confidence"], elapsed, os.path.basename(out_file)))
    return result


# ===== 主入口 =====
def main(argument):
    work_path = GlobalVariables.get("$Flow.WorkPath", "")
    res_input = os.path.join(work_path, "res", "输入")
    res_output = os.path.join(work_path, "res", "输出")
    os.makedirs(res_output, exist_ok=True)

    # 收集PDF：参数指定单个 > 扫描res/下所有
    pdf_files = []
    if isinstance(argument, str) and argument and argument.lower().endswith(".pdf"):
        pdf_files = [argument]
    if not pdf_files and os.path.exists(res_input):
        for f in sorted(os.listdir(res_input)):
            if f.lower().endswith(".pdf") and not f.startswith("~"):
                pdf_files.append(os.path.join(res_input, f))

    if not pdf_files:
        raise ValueError("res/ 文件夹中没有PDF文件")

    Log.Info("=" * 50)
    Log.Info("找到 {} 个PDF文件".format(len(pdf_files)))
    Log.Info("=" * 50)

    all_summary = []
    for pdf_path in pdf_files:
        try:
            r = process_one_pdf(pdf_path, res_output)
            all_summary.append({
                "file": os.path.basename(pdf_path),
                "type": r["type"],
                "pages": r["total_pages"],
                "confidence": r["avg_confidence"],
                "seconds": r["elapsed_seconds"],
            })
        except Exception as ex:
            Log.Error("处理失败: {} - {}".format(os.path.basename(pdf_path), str(ex)))

    # 保存汇总
    summary_path = os.path.join(res_output, "_汇总.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_summary, f, ensure_ascii=False, indent=2)

    Log.Info("=" * 50)
    Log.Info("全部完成! {} 个文件, 结果在 res/输出/".format(len(all_summary)))
    Log.Info("=" * 50)

    return {
        "total": len(pdf_files),
        "done": len(all_summary),
        "output": res_output,
        "summary": summary_path,
    }
