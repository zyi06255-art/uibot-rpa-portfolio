# PDF OCR 识别系统 / PDF OCR Recognition System

## 项目简介

多策略 PDF 文字提取系统。根据 PDF 类型（数字版/扫描版）自动选择最优策略：数字 PDF 用 PyMuPDF 直接提取嵌入文字，扫描件用 PaddleOCR 进行光学字符识别。支持承兑汇票、发票、合同等多种文档类型。

## 技术架构

```
PDF 输入
  ├─ 类型检测 (前3页文字量)
  │
  ├─ 数字 PDF → PyMuPDF (fitz) 提取嵌入文字 → 结构化 JSON
  │   └─ 按坐标排序, 保留位置信息
  │
  └─ 扫描件 PDF → 转图片 (200 DPI) → PaddleOCR → 结构化 JSON
      └─ 可选: OpenCV 红章去除 → 提高准确率
```

## 核心亮点

### 1. 智能类型检测

`detect_pdf_type()` 函数通过前 3 页的文字量自动判断 PDF 类型：
- 总字符数 ≥ 50 → 数字 PDF（有嵌入文字层）
- 总字符数 < 50 → 扫描件（需要 OCR）

### 2. 双引擎 OCR

| 引擎 | 适用场景 | 文件 |
|------|---------|------|
| PyMuPDF (fitz) | 数字 PDF | `PDF识别.py` |
| PaddleOCR | 扫描件 / 图片 | `ocr_paddle.py`, `PDF识别.py` |

### 3. OCR 质量评估

`ocr_eval.py` 和 `ocr_eval_v2.py` 提供 OCR 结果的量化评估：
- 字符级准确率
- 字段级提取准确率
- 与标注 Ground Truth 的对比

### 4. 草案提取

`extract_draft_dict.py` 针对电子商业承兑汇票的特定字段提取：
- 出票人、收票人
- 汇票金额
- 承兑日期
- 到期日期

## 文件说明

| 文件 | 角色 |
|------|------|
| `PDF识别.py` | **核心**：PDF 类型检测 + 双策略识别主流程 |
| `ocr_paddle.py` | PaddleOCR 封装 + 红章去除预处理 |
| `ocr_eval.py` | OCR 识别结果评估 (v1) |
| `ocr_eval_v2.py` | OCR 识别结果评估 (v2, 增强版) |
| `extract_draft_dict.py` | 承兑汇票结构化字段提取 |
| `run_all_paddle.py` | 批量 OCR 运行脚本 |
| `generate_doc.py` | Word 文档生成器 |
| `CLAUDE-NEW.md` | 知识库（项目专属） |
| `uibot-api-full.md` | UiBot API 完整参考 |
| `flow-requirements.md` | 流程需求文档 |
| `环境配置-稳定版本.txt` | 依赖包稳定版本号 |

## 环境配置

参考 `环境配置-稳定版本.txt` 中的稳定版本号安装依赖：

```bash
pip install pymupdf paddleocr opencv-python pillow numpy
```

**注意**：PaddleOCR 在 Windows 上需禁用 oneDNN：
```python
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["KMP_AFFINITY"] = "disabled"
```

## 示例输出

```json
{
  "file": "承兑汇票.pdf",
  "type": "scanned",
  "total_pages": 1,
  "avg_confidence": 96.5,
  "elapsed_seconds": 3.2,
  "pages": [{
    "page": 1,
    "count": 24,
    "avg_confidence": 96.5,
    "items": [
      {"text": "电子商业承兑汇票", "x": 300, "y": 50, "conf": 0.99}
    ]
  }]
}
```
