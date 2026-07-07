import os, json, copy, decimal, random
import pandas as pd
import requests
from io import StringIO
from apa_runtime import *

# ===================== 配置 =====================
STOCK_CODE = "000726"
STOCK_NAME = "鲁泰A"
SAVE_FOLDER = ""

# 关键请求头（必须加，否则新浪直接拒绝访问）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Referer": "https://finance.sina.com.cn/",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# ===================== 报表URL配置 =====================
REPORTS_CONFIG = {
    2023: {
        "资产负债表": "https://money.finance.sina.com.cn/corp/go.php/vFD_BalanceSheet/stockid/000726/ctrl/2023/displaytype/4.phtml",
        "利润表": "https://money.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/000726/ctrl/2023/displaytype/4.phtml",
        "现金流量表": "https://money.finance.sina.com.cn/corp/go.php/vFD_CashFlow/stockid/000726/ctrl/2023/displaytype/4.phtml",
    },
    2024: {
        "资产负债表": "https://money.finance.sina.com.cn/corp/go.php/vFD_BalanceSheet/stockid/000726/ctrl/2024/displaytype/4.phtml",
        "利润表": "https://money.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/000726/ctrl/2024/displaytype/4.phtml",
        "现金流量表": "https://money.finance.sina.com.cn/corp/go.php/vFD_CashFlow/stockid/000726/ctrl/2024/displaytype/4.phtml",
    },
    2025: {
        "资产负债表": "https://money.finance.sina.com.cn/corp/go.php/vFD_BalanceSheet/stockid/000726/ctrl/2025/displaytype/4.phtml",
        "利润表": "https://money.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/000726/ctrl/2025/displaytype/4.phtml",
        "现金流量表": "https://money.finance.sina.com.cn/corp/go.php/vFD_CashFlow/stockid/000726/ctrl/2025/displaytype/4.phtml",
    }
}

# ===================== 抓取单个报表 =====================
def fetch_report(report_name, url):
    """抓取单个报表，返回DataFrame"""
    try:
        print("   正在抓取：{}".format(report_name))

        res = requests.get(url, headers=HEADERS, timeout=10)
        res.encoding = "gbk"

        if res.status_code != 200:
            print("   ❌ 请求失败，状态码：{}".format(res.status_code))
            return None

        html_io = StringIO(res.text)
        dfs = pd.read_html(html_io)

        df = None
        for idx, table in enumerate(dfs):
            if len(table) > 10 and len(table.columns) >= 2:
                first_col = table.iloc[:, 0].astype(str)
                keywords = []
                if report_name == "资产负债表":
                    keywords = ['资产', '负债', '权益', '货币资金', '应收账款']
                elif report_name == "利润表":
                    keywords = ['营业收入', '营业成本', '利润', '净利润', '每股收益']
                elif report_name == "现金流量表":
                    keywords = ['经营活动', '投资活动', '筹资活动', '现金', '现金流量']

                if any(keyword in ' '.join(first_col[:10]) for keyword in keywords):
                    df = table
                    print("   ✅ 找到{}表格，形状：{}".format(report_name, table.shape))
                    break

        if df is None:
            for table in dfs:
                if len(table) > 10 and len(table.columns) >= 2:
                    df = table
                    print("   ✅ 找到{}表格（默认），形状：{}".format(report_name, table.shape))
                    break

        if df is None:
            print("   ❌ 未找到{}表格".format(report_name))
            return None

        start_row = 0
        for i in range(min(5, len(df))):
            first_cell = str(df.iloc[i, 0])
            if '项目' in first_cell or '科目' in first_cell or '报告期' in first_cell:
                start_row = i + 1
                break

        if len(df.columns) >= 2:
            df_clean = df.iloc[start_row:, [0, 1]].copy()
            df_clean.columns = ["项目", "金额"]
        else:
            df_clean = df.iloc[start_row:, :].copy()
            df_clean.columns = ["项目", "金额"] if len(df_clean.columns) == 2 else ["项目"]

        df_clean = df_clean.dropna(how='all')
        if '项目' in df_clean.columns:
            df_clean = df_clean[df_clean['项目'].notna()]
            df_clean['项目'] = df_clean['项目'].astype(str).str.strip()

        if '金额' in df_clean.columns:
            df_clean['金额'] = df_clean['金额'].astype(str).str.replace(',', '')
            df_clean['金额'] = df_clean['金额'].str.replace('--', '0')
            df_clean['金额'] = df_clean['金额'].str.replace('—', '0')

        print("   ✅ {}抓取成功，共{}行数据".format(report_name, len(df_clean)))
        return df_clean

    except Exception as e:
        print("   ❌ 抓取{}失败：{}".format(report_name, str(e)))
        return None

# ===================== 保存年度Excel文件 =====================
def save_year_excel(year, reports_data):
    """将一年的所有报表保存到一个Excel文件的不同工作表中"""
    filename = "{}{}年度财务报表.xlsx".format(STOCK_NAME, year)
    save_path = os.path.join(SAVE_FOLDER, filename)

    try:
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            for report_name, df in reports_data.items():
                if df is not None and not df.empty:
                    df.to_excel(writer, sheet_name=report_name, index=False)

                    worksheet = writer.sheets[report_name]
                    worksheet.column_dimensions['A'].width = 30
                    worksheet.column_dimensions['B'].width = 20

        print("\n✅ 保存成功：{}（包含{}个报表）".format(filename, len(reports_data)))
        return True
    except Exception as e:
        print("\n❌ 保存{}失败：{}".format(filename, str(e)))
        return False

# ===================== 主函数 =====================
def main(argument):
    global SAVE_FOLDER
    SAVE_FOLDER = GlobalVariables["$Flow.ResPath"]
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    print("=" * 60)
    print("【{}】2023-2025年财务报表抓取".format(STOCK_NAME))
    print("=" * 60)
    print("保存路径：{}\n".format(SAVE_FOLDER))

    success_years = []

    for year, reports in REPORTS_CONFIG.items():
        print("\n--- 抓取 {} 年数据 ---".format(year))
        reports_data = {}

        for report_name, url in reports.items():
            df = fetch_report(report_name, url)
            reports_data[report_name] = df

        if any(df is not None for df in reports_data.values()):
            if save_year_excel(year, reports_data):
                success_years.append(year)
        else:
            print("\n❌ {}年所有报表抓取失败".format(year))

    print("\n" + "=" * 60)
    print("抓取完成！")
    print("=" * 60)

    if success_years:
        print("✅ 成功保存年份：{}".format(success_years))
        print("\n生成的文件：")
        for year in success_years:
            filename = "{}{}年度财务报表.xlsx".format(STOCK_NAME, year)
            filepath = os.path.join(SAVE_FOLDER, filename)
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath) / 1024
                print("  📄 {} ({} KB)".format(filename, round(file_size, 1)))
    else:
        print("❌ 所有年份抓取失败，请检查网络或稍后重试")

    print("\n文件保存位置：{}".format(SAVE_FOLDER))
