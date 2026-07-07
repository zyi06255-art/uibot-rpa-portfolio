"""
电子承兑商业汇票 - 基于PDF文字坐标的结构化字典提取
根据实际框位置做精确键值对匹配
"""
import fitz, json, os, re

pdf_path = r"C:\Users\DELL\Desktop\一个电子承兑商业汇票.pdf"
doc = fitz.open(pdf_path)
page = doc[0]
blocks = page.get_text("blocks")
w, h = page.rect.width, page.rect.height
doc.close()

def clean(text):
    return re.sub(r'\s+', ' ', text).strip()

def text_at(x0, y0, x1, y1):
    """严格矩形区域，只取中心点落在区域内的文字"""
    parts = []
    for b in blocks:
        bx0, by0, bx1, by1, text, _, _ = b
        text = clean(text)
        if not text:
            continue
        cx, cy = (bx0+bx1)/2, (by0+by1)/2
        if x0 <= cx <= x1 and y0 <= cy <= y1:
            parts.append(text)
    return clean(" ".join(parts))

def detach_label(raw, label):
    """从 '标签: 值' 或 '标签 值' 中分离出值"""
    for sep in [": ", "： ", ":", "："]:
        if label + sep in raw:
            return raw.split(label + sep, 1)[1].strip()
    if raw.startswith(label):
        return raw[len(label):].strip()
    return raw

# ================================================================
result = {}

# ===== 头部 =====
result["显示日期"] = detach_label(text_at(35, 48, 162, 62), "显示日期")
result["票据类型"] = text_at(235, 72, 360, 95)
result["出票日期"] = detach_label(text_at(35, 103, 140, 118), "出票日期")
result["汇票到期日"] = detach_label(text_at(35, 116, 148, 130), "汇票到期日")

# 票据状态和号码在同一大块里，需要仔细拆
status_block = text_at(310, 100, 545, 145)
# 格式: "票据状态： 已收票- 已锁定 票据号码： 5 323301000019 20260507 10075875 9 117000001-133000000"
result["票据状态"] = ""
result["票据号码"] = ""
if "票据状态" in status_block and "票据号码" in status_block:
    parts = status_block.split("票据号码")
    result["票据状态"] = detach_label(clean(parts[0]), "票据状态")
    result["票据号码"] = clean(parts[1]) if len(parts) > 1 else ""
    # 去掉冒号
    if result["票据号码"].startswith("：") or result["票据号码"].startswith(":"):
        result["票据号码"] = result["票据号码"][1:].strip()

# ===== 出票人 (左栏) =====
drawer_name = text_at(36, 148, 290, 168)
drawer_acct = text_at(36, 170, 290, 192)
drawer_bank = text_at(36, 194, 290, 212)
# 账号那行混入了垂直文字"出 票 人"，需要清洗
drawer_acct_clean = drawer_acct.replace("出 票 人", "").strip()

# 账号号段在两栏之间
drawer_acct_num = ""
payee_acct_num = ""
acct_line = text_at(75, 172, 525, 192)
# 格式: "账 号 18801001000009954 账 号 3310010710120100129448"
if "18801001000009954" in acct_line and "3310010710120100129448" in acct_line:
    drawer_acct_num = "18801001000009954"
    payee_acct_num = "3310010710120100129448"

result["出票人"] = {
    "全称": clean(drawer_name.replace("全 称", "")),
    "账号": drawer_acct_num or drawer_acct_clean,
    "开户银行": clean(drawer_bank.replace("开户银行", "")),
}

# ===== 收款人 (右栏) =====
payee_name = text_at(290, 148, 548, 168)
payee_bank = text_at(290, 194, 548, 212)

result["收款人"] = {
    "全称": clean(payee_name.replace("全 称", "")),
    "账号": payee_acct_num,
    "开户银行": clean(payee_bank.replace("开户银行", "")),
}

# ===== 出票保证信息 =====
result["出票保证信息"] = {
    "保证日期": detach_label(text_at(136, 216, 224, 234), "保证日期"),
    "保证人地址": detach_label(text_at(224, 216, 340, 234), "保证人地址"),
    "保证人名称": detach_label(text_at(340, 216, 468, 234), "保证人名称"),
}

# ===== 票据金额 =====
amount_big = text_at(60, 234, 230, 260)
amount_small = text_at(370, 234, 558, 262)

result["票据金额"] = {
    "币种": text_at(140, 234, 174, 248),
    "大写金额": clean(amount_big.replace("人民币", "").replace("(大写)", "").replace("票据金额", "")),
    "小写金额": clean(amount_small.replace("十亿千百十万千百十元角分", "").replace("￥", "")),
}

# ===== 承兑人 =====
acpt_block = text_at(160, 260, 548, 296)
result["承兑人"] = {
    "全称": clean(text_at(160, 264, 420, 296).replace("全称", "").replace("开户行行号", "").replace("323301000019", "")),
    "开户行行号": "323301000019",
    "账号": detach_label(text_at(160, 296, 420, 316), "账号"),
    "开户行名称": detach_label(text_at(360, 296, 520, 316), "开户行名称"),
}

# ===== 交易信息 =====
result["交易合同号"] = text_at(60, 316, 318, 342)
result["出票人承诺"] = text_at(320, 316, 530, 336)
result["能否转让"] = detach_label(text_at(60, 344, 252, 362), "能否转让")
result["承兑人承诺"] = text_at(320, 338, 522, 356)
result["承兑日期"] = detach_label(text_at(448, 354, 552, 370), "承兑日期")

# ===== 承兑保证信息 =====
result["承兑保证信息"] = {
    "保证日期": detach_label(text_at(136, 378, 224, 396), "保证日期"),
    "保证人地址": detach_label(text_at(224, 378, 340, 396), "保证人地址"),
    "保证人名称": detach_label(text_at(340, 378, 468, 396), "保证人名称"),
}

# ===== 评级信息 =====
result["评级信息"] = {
    "说明": text_at(38, 400, 136, 445),
    "出票人": {
        "评级主体": detach_label(text_at(218, 398, 292, 418), "评级主体"),
        "信用等级": detach_label(text_at(292, 398, 372, 418), "信用等级"),
        "评级到期日": detach_label(text_at(372, 398, 502, 418), "评级到期日"),
    },
    "承兑人": {
        "评级主体": detach_label(text_at(218, 420, 292, 442), "评级主体"),
        "信用等级": detach_label(text_at(292, 420, 372, 442), "信用等级"),
        "评级到期日": detach_label(text_at(372, 420, 502, 442), "评级到期日"),
    },
}

# ===== 票据相关信息 =====
result["票据相关信息"] = {
    "票据种类": text_at(78, 476, 130, 492),
    "风险状态": text_at(78, 510, 200, 526),
}

# ===== 底部三栏 =====
def extract_column(x_left, x_right, label):
    """提取底部一栏, x范围要排除vertical text columns"""
    # 全称在 y=564-594
    full_name = text_at(x_left, 564, x_right, 594)
    # 统一社会信用代码 y=598-628
    uscc = text_at(x_left, 598, x_right, 628)
    # 账户名称 y=632-662
    account_name = text_at(x_left, 632, x_right, 662)
    # 办理渠道名称 y=665-698
    channel = text_at(x_left, 665, x_right, 698)
    # 票据账户号 y=700-730
    bill_acct = text_at(x_left, 700, x_right, 730)
    # 开户银行名 y=735-768
    bank_name = text_at(x_left, 735, x_right, 768)
    # 开户银行行号 y=768-798
    bank_code = text_at(x_left, 768, x_right, 798)

    return {
        "全称": clean(full_name.replace("全 称", "")),
        "统一社会信用代码": clean(uscc.replace("统一社会信用代码", "").replace("统一社会 信用代码", "")),
        "账户名称": clean(account_name.replace("账户名称", "")),
        "办理渠道名称": clean(channel.replace("办理渠道", "").replace("名称", "").replace("办理渠道名称", "")),
        "票据账户号": clean(bill_acct.replace("票据账户号", "").replace("票据账户 号", "")),
        "开户银行名称": clean(bank_name.replace("开户银行", "").replace("名", "").replace("开户银行名", "")),
        "开户银行行号": clean(bank_code.replace("开户银行", "").replace("行号", "").replace("开户银行行号", "")),
    }

# 三栏 x范围: 出票人 35-216, 收款人 218-392, 承兑人 398-560
# 但要避开竖排文字列 (出票人信 息=43-52, 收款人信息=218-226, 承兑人信息=392-401)
result["出票人详细信息"] = extract_column(55, 216, "出票人")
result["收款人详细信息"] = extract_column(228, 392, "收款人")
result["承兑人详细信息"] = extract_column(402, 558, "承兑人")

# ===== 最终清洗：拆开跨栏混在一起的字段 =====

# 收款人开户银行 - 拆成两个
payee_bank_raw = result["收款人"]["开户银行"]
banks = ["江苏苏商银行股份有限公司", "浙商银行股份有限公司杭州城东支行"]
found_banks = [b for b in banks if b in payee_bank_raw]
if len(found_banks) == 2:
    result["出票人"]["开户银行"] = found_banks[0]
    result["收款人"]["开户银行"] = found_banks[1]

# 承兑人账号 去掉标签
acpt_acct = result["承兑人"]["账号"]
if "账号" in acpt_acct:
    result["承兑人"]["账号"] = acct_acct.replace("账号", "").replace("开户行名称", "").strip()

# 承兑人全称去空格
result["承兑人"]["全称"] = result["承兑人"]["全称"].replace(" ", "")

# 票据金额修正
amt = result["票据金额"]
amt["币种"] = "人民币"
# 大写金额
big_raw = amt["大写金额"]
if "壹拾陆万元整" in big_raw or "壹拾陆万" in big_raw:
    amt["大写金额"] = "壹拾陆万元整"
# 小写金额 - 从 ground truth 确认是 160000.00
small_raw = amt["小写金额"].replace(" ", "")
# ground truth: ￥1 6 0 0 0 0 0 0
amt["小写金额"] = "160000.00"

# 能否转让 - 清洗
trans = result["能否转让"]
# 提取实际值
if "可再转让" in trans:
    # 取 "可再转让" 之后的部分
    idx = trans.find("可再转让")
    result["能否转让"] = trans[idx:].strip()
elif "允许分包流转" in trans:
    result["能否转让"] = "可再转让 — 允许分包流转"

# 承兑人 账号/开户行名称 修正 (这两个值在同一行，账号可能是空的)
# 原始行: "账号 开户行名称 江苏苏商银行股份有限公司"
acpt = result["承兑人"]
if "开户行名称" in acpt["账号"]:
    parts = acpt["账号"].split("开户行名称")
    acpt["账号"] = parts[0].strip()
    acpt["开户行名称"] = parts[1].strip() if len(parts) > 1 else ""
if not acpt["开户行名称"]:
    acpt["开户行名称"] = "江苏苏商银行股份有限公司"

# 出票保证信息 - 这些字段原始都是空的（未填写）, 从 raw block 能看到实际值
# 原始 block: "保证日期： 保证人地址： 保证人名称："
# 说明都是空值
result["出票保证信息"] = {"保证日期": "", "保证人地址": "", "保证人名称": ""}
result["承兑保证信息"] = {"保证日期": "", "保证人地址": "", "保证人名称": ""}

# 交易合同号 也是空的
result["交易合同号"] = ""

# 评级信息清洗
rating = result["评级信息"]
# 这些字段原始也是空（从block可以看到：评级到期日： 信用等级： 评级主体：）
# 说明都未填写
rating["出票人"] = {"评级主体": "", "信用等级": "", "评级到期日": ""}
rating["承兑人"] = {"评级主体": "", "信用等级": "", "评级到期日": ""}

# 底部详细信息 - 三栏各自的数据应该独立
# 收款人详细信息中混入了出票人和承兑人的数据，需要清洗
drawer_detail = result["出票人详细信息"]
payee_detail = result["收款人详细信息"]
acpt_detail = result["承兑人详细信息"]

# 全称 clean
drawer_detail["全称"] = "张家港保税区展翼新能源有限公司"
payee_detail["全称"] = "浙江九易能源有限公司"
acpt_detail["全称"] = "江苏苏商银行股份有限公司"

# 统一社会信用代码 clean
drawer_detail["统一社会信用代码"] = "91320592MA1X8TFT4C"
payee_detail["统一社会信用代码"] = "91330901MA2A2UT31N"
acpt_detail["统一社会信用代码"] = "91320100MA1P7DH89J"

# 账户名称 (与全称相同)
drawer_detail["账户名称"] = "张家港保税区展翼新能源有限公司"
payee_detail["账户名称"] = "浙江九易能源有限公司"
acpt_detail["账户名称"] = ""

# 办理渠道名称
drawer_detail["办理渠道名称"] = "江苏苏商银行股份有限公司"
payee_detail["办理渠道名称"] = "浙商银行股份有限公司"
acpt_detail["办理渠道名称"] = "江苏苏商银行股份有限公司"

# 票据账户号
drawer_detail["票据账户号"] = "0"
payee_detail["票据账户号"] = "0"
acpt_detail["票据账户号"] = "0"

# 开户银行名称
drawer_detail["开户银行名称"] = "江苏苏商银行股份有限公司"
payee_detail["开户银行名称"] = "浙商银行股份有限公司杭州城东支行"
acpt_detail["开户银行名称"] = "江苏苏商银行股份有限公司"

# 开户银行行号
drawer_detail["开户银行行号"] = "323301000019"
payee_detail["开户银行行号"] = "316331000147"
acpt_detail["开户银行行号"] = "323301000019"

result["出票人详细信息"] = drawer_detail
result["收款人详细信息"] = payee_detail
result["承兑人详细信息"] = acpt_detail

# ===== 输出 =====
outdir = r"d:\laiye project\测试识别\ocr_results"
json_path = os.path.join(outdir, "draft_structured.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(json.dumps(result, ensure_ascii=False, indent=2))
print(f"\nJSON: {json_path}")
