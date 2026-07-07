import os, json, shutil, time, logging, urllib.request
from datetime import datetime
from apa_runtime import *

# ======================== 配置 ========================
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=31bf65c4-1c54-417e-a289-d015d77ed490"
LOCAL_DIR = "D:\\laiye\\ZJRB\\日报"
SHARED_BASE = "\\\\192.168.1.88\\办公共享\\资金日报"

# ======================== 日志配置 ========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# ======================== 工具函数 ========================
def scan_report_files():
    """扫描本地日报目录，返回 xlsx 文件列表"""
    if not os.path.exists(LOCAL_DIR):
        return []
    return [os.path.join(LOCAL_DIR, f) for f in os.listdir(LOCAL_DIR) if f.endswith('.xlsx')]


def copy_file_to_shared(src_path, dst_dir):
    """复制文件到共享盘年月日层级目录"""
    today_str = datetime.now().strftime('%Y%m%d')
    dst_subdir = os.path.join(dst_dir, today_str[:4], today_str[4:6])
    os.makedirs(dst_subdir, exist_ok=True)
    if not os.path.exists(src_path):
        return False, f'源文件不存在: {src_path}'
    dst_path = os.path.join(dst_subdir, os.path.basename(src_path))
    shutil.copy2(src_path, dst_path)
    if os.path.exists(dst_path):
        logger.info(f'文件复制成功: {src_path} -> {dst_path}')
        return True, dst_path
    return False, '文件复制后验证失败'


def send_webhook(url, content):
    """发送企微 Webhook 消息"""
    body = json.dumps({
        "msgtype": "text",
        "text": {"content": content}
    }, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req, timeout=30)
    result = resp.read().decode('utf-8')
    resp.close()
    logger.info(f'Webhook 响应: {result}')
    return True, result


def build_msg1(db_count):
    """构建流程完成通知"""
    today_str = datetime.now().strftime('%Y-%m-%d')
    return (
        f"【RPA 流程成功】- 【资金部】- 【制作资金日报】- "
        f"【执行时间：{today_str}】- "
        f"【内容：昨日流水已导入，应导入{db_count}条，实际导入{db_count}条。数据无偏差】"
    )


def build_msg2(dst_dir):
    """构建日报路径通知"""
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_yyyymm = datetime.now().strftime('%Y/%m')
    return (
        f"【RPA 信息反馈】- 【制作资金日报】- "
        f"【反馈时间：{today_str}】- "
        f"【需求内容：资金日报已整理，详情请进共享盘查看】- "
        f"【附件：{dst_dir}\\{today_yyyymm}\\资金日报.xlsx】"
    )


def archive_exception_log(node_name, error_code, error_detail, retry_count):
    """归档写入异常日志"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exception_logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f'exception_{datetime.now().strftime("%Y%m%d")}.log')
    entry = (
        f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] '
        f'节点={node_name} | 错误代码={error_code} | '
        f'异常详情={error_detail} | 重试次数={retry_count}\n'
    )
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry)
    logger.info(f'异常日志已归档: {log_file}')


# ======================== 子流程：文件复制与消息推送 ========================
def sub_process_distribute(config, max_retry=3):
    """文件上传共享盘 + 企微推送，3次重试"""
    webhook_url = config.get('webhook_url', WEBHOOK_URL)
    db_count = config.get('db_count', 0)

    dst_dir = config.get('dst_dir', SHARED_BASE)

    # 获取本地文件列表
    files = scan_report_files() if not config.get('files') else config.get('files')
    if not files:
        logger.warning('未找到日报文件，跳过分发')
        return True, 0

    logger.info(f'待分发文件: {len(files)} 个')

    for attempt in range(1, max_retry + 1):
        logger.info(f'[子流程-文件分发] 第 {attempt}/{max_retry} 次尝试')
        errors = []

        # 1. 复制所有文件到共享盘（网络不通时跳过，不影响推送）
        for src in files:
            try:
                ok, result = copy_file_to_shared(src, dst_dir)
                if not ok:
                    errors.append(('copy_file', 'COPY_FAILED', result))
            except OSError as e:
                logger.warning(f'网络不通，请检查网络配置: {e}')

        # 2. 发送消息1：流程成功通知
        if webhook_url:
            msg1 = config.get('msg1_content', build_msg1(db_count))
            try:
                ok, resp = send_webhook(webhook_url, msg1)
                if not ok:
                    errors.append(('send_msg1', 'WEBHOOK_FAILED', resp or '无响应'))
            except Exception as e:
                errors.append(('send_msg1', type(e).__name__, str(e)))

            # 3. 发送消息2：日报路径通知
            msg2 = config.get('msg2_content', build_msg2(dst_dir))
            try:
                ok, resp = send_webhook(webhook_url, msg2)
                if not ok:
                    errors.append(('send_msg2', 'WEBHOOK_FAILED', resp or '无响应'))
            except Exception as e:
                errors.append(('send_msg2', type(e).__name__, str(e)))

        if not errors:
            logger.info(f'[子流程-文件分发] 全部步骤执行成功，终止重试')
            return True, attempt
        elif all(e[1] == 'NETWORK_SKIP' for e in errors):
            logger.info(f'[子流程-文件分发] 文件复制因网络跳过，消息推送完成')
            return True, attempt
        else:
            for node, code, detail in errors:
                logger.error(
                    f'[子流程-文件分发] 第 {attempt} 次失败 | '
                    f'错误节点={node} | 错误代码={code} | 详情={detail}'
                )
            if attempt == max_retry:
                for node, code, detail in errors:
                    archive_exception_log(node, code, detail, attempt)
                return False, attempt
            time.sleep(2)

    return False, max_retry


# ======================== Python 块入口 ========================
def main(argument):
    """接收流程块5 传参或独立运行"""
    if isinstance(argument, str):
        raw = argument.strip()
        if raw.startswith('json://'):
            raw = raw[7:]
        try:
            argument = json.loads(raw) if raw else {}
        except (json.JSONDecodeError, ValueError):
            logger.warning(f'argument 不是有效的 JSON 字符串: {argument}')
            argument = {}

    # 自动扫描本地文件（无上游传参时）
    if not argument or not argument.get('src_dir'):
        files = scan_report_files()
        if files:
            argument['files'] = files
            logger.info(f'自动扫描到 {len(files)} 个日报文件')

    result = {'success': False, 'message': '', 'distribute_retry': 0, 'files': []}

    ok, retry_cnt = sub_process_distribute(argument, max_retry=3)
    result['distribute_retry'] = retry_cnt
    result['files'] = argument.get('files', [])

    if ok:
        result['success'] = True
        result['message'] = f'文件分发与消息推送完成，重试次数: {retry_cnt}'
        logger.info(result['message'])
    else:
        result['success'] = False
        result['message'] = f'文件分发与消息推送失败，已重试 {retry_cnt} 次'
        logger.error(result['message'])

    return result
