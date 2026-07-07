import os, json, copy, decimal, random, time, logging
from datetime import datetime
from apa_runtime import *


# ======================== 日志配置 ========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# ======================== 工具函数 ========================
def close_office_windows():
    """关闭前台 Excel/WPS 及无关办公窗口，清理后台残留进程"""
    office_processes = ['EXCEL.EXE', 'et.exe', 'wps.exe', 'wpp.exe', 'POWERPNT.EXE', 'WINWORD.EXE']
    killed = []
    for proc_name in office_processes:
        exit_code = os.system(f'taskkill /f /im {proc_name} 2>nul')
        if exit_code == 0:
            killed.append(proc_name)
            logger.info(f'已终止进程: {proc_name}')
    return killed


def sync_server_time(server='time.windows.com'):
    """同步服务器时间，校准本地时差"""
    try:
        os.system(f'w32tm /resync /computer:{server} /nowait')
        logger.info(f'时间同步完成，目标服务器: {server}')
        return True, None
    except Exception as e:
        return False, str(e)


def set_standard_resolution():
    """设置标准分辨率"""
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.ChangeDisplaySettingsW(None, 0)
        logger.info(f'分辨率已恢复为默认设置')
        return True, None
    except Exception as e:
        return False, str(e)


def disable_screensaver_and_lock():
    """关闭屏保与自动锁屏"""
    try:
        os.system('powercfg /change monitor-timeout-ac 0')
        os.system('powercfg /change monitor-timeout-dc 0')
        os.system('powercfg /change standby-timeout-ac 0')
        os.system('powercfg /change standby-timeout-dc 0')
        os.system('reg add "HKCU\\Control Panel\\Desktop" /v ScreenSaveActive /t REG_SZ /d 0 /f')
        os.system('reg add "HKCU\\Control Panel\\Desktop" /v ScreenSaveTimeOut /t REG_SZ /d 0 /f')
        logger.info('屏保与自动锁屏已关闭')
        return True, None
    except Exception as e:
        return False, str(e)


def test_mysql_connection(host, port, user, password, database, timeout=5):
    """创建 MySQL 连接会话并做连通性测试"""
    try:
        import pymysql
        conn = pymysql.connect(
            host=host, port=port, user=user, password=password,
            database=database, connect_timeout=timeout
        )
        conn.ping(reconnect=False)
        conn.close()
        logger.info(f'MySQL 连接测试成功 {host}:{port}/{database}')
        return True, None, None
    except ImportError:
        return False, 'IMPORT_ERROR', '缺少 pymysql 模块，请通过 pip install pymysql 安装'
    except Exception as e:
        error_code = type(e).__name__
        error_detail = str(e)
        logger.error(f'MySQL 连接失败 [{error_code}] {error_detail}')
        return False, error_code, error_detail


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


# ======================== 子流程：关闭办公窗口 ========================
def sub_process_close_office(max_retry=3):
    """
    子流程：关闭前台 Excel/WPS 及无关办公窗口，清理后台残留进程
    固定 3 次循环重试，执行正常则标记已完成并结束重试
    """
    for attempt in range(1, max_retry + 1):
        logger.info(f'[子流程-关闭办公窗口] 第 {attempt}/{max_retry} 次尝试')
        try:
            killed = close_office_windows()
            if killed:
                logger.info(f'[子流程-关闭办公窗口] 执行成功，已终止进程: {killed}，结束重试')
                return True, attempt
            else:
                logger.info(f'[子流程-关闭办公窗口] 未发现残留进程，视为执行成功，结束重试')
                return True, attempt
        except Exception as e:
            error_code = type(e).__name__
            error_detail = str(e)
            logger.error(
                f'[子流程-关闭办公窗口] 第 {attempt} 次失败 | '
                f'错误节点=close_office_windows | 错误代码={error_code} | 详情={error_detail}'
            )
            if attempt == max_retry:
                archive_exception_log('close_office_windows', error_code, error_detail, attempt)
                return False, attempt
            time.sleep(2)

    return False, max_retry


# ======================== 子流程：初始化环境 ========================
def sub_process_init_env(mysql_config, max_retry=3):
    """
    子流程：同步时间、设置分辨率、关闭屏保、测试 MySQL 连接
    固定 3 次循环重试，任意步骤正常则标记无异常并结束重试
    """
    for attempt in range(1, max_retry + 1):
        logger.info(f'[子流程-环境初始化] 第 {attempt}/{max_retry} 次尝试')
        errors = []

        ok, err = sync_server_time()
        if not ok:
            errors.append(('sync_server_time', 'SYNC_FAILED', err))
        else:
            time.sleep(0.5)

        ok, err = set_standard_resolution()
        if not ok:
            errors.append(('set_standard_resolution', 'RESOLUTION_FAILED', err))
        else:
            time.sleep(0.5)

        ok, err = disable_screensaver_and_lock()
        if not ok:
            errors.append(('disable_screensaver_and_lock', 'POWERCFG_FAILED', err))
        else:
            time.sleep(0.5)

        ok, error_code, error_detail = test_mysql_connection(**mysql_config)
        if not ok:
            errors.append(('test_mysql_connection', error_code, error_detail))

        if not errors:
            logger.info(f'[子流程-环境初始化] 全部步骤执行成功，终止重试')
            return True, attempt
        else:
            for node, code, detail in errors:
                logger.error(
                    f'[子流程-环境初始化] 第 {attempt} 次失败 | '
                    f'错误节点={node} | 错误代码={code} | 详情={detail}'
                )
            if attempt == max_retry:
                for node, code, detail in errors:
                    archive_exception_log(node, code, detail, attempt)
                return False, attempt
            time.sleep(3)

    return False, max_retry


# ======================== Python 块入口 ========================
def main(argument):
    """
    argument 支持两种形式:
        - JSON 字符串: '{"t_processinfo": "...", "mysql_config": {...}}'
        - dict 直传:    {"t_processinfo": "...", "mysql_config": {...}}
    字段说明:
        t_processinfo: str  — 流程状态标记，"已完成" 则直接退出
        mysql_config: dict — {host, port, user, password, database}
    """
    # 兼容 UiBot 传入 JSON 字符串（可能带 json:// 前缀）的情况
    if isinstance(argument, str):
        raw = argument.strip()
        if raw.startswith('json://'):
            raw = raw[7:]
        try:
            argument = json.loads(raw) if raw else {}
        except (json.JSONDecodeError, ValueError):
            logger.warning(f'argument 不是有效的 JSON 字符串，按空配置处理: {argument}')
            argument = {}

    result = {
        'success': False,
        'message': '',
        'close_office_retry': 0,
        'init_env_retry': 0
    }

    # —————— 第1步：校验 t_processinfo ——————
    t_processinfo = argument.get('t_processinfo', '')
    if t_processinfo == '已完成':
        result['success'] = True
        result['message'] = '流程已完成，跳过本次执行'
        logger.info(result['message'])
        return result

    # —————— 第2步：子流程 — 关闭办公窗口（3次重试）——————
    ok, retry_cnt = sub_process_close_office(max_retry=3)
    result['close_office_retry'] = retry_cnt

    if not ok:
        result['success'] = False
        result['message'] = f'关闭办公窗口失败，已重试 {retry_cnt} 次，终止全流程'
        logger.error(result['message'])
        return result

    # —————— 第3步：子流程 — 环境初始化（3次重试）——————
    mysql_config = argument.get('mysql_config', {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'rpa_bank_flow',
        'timeout': 5
    })

    ok, retry_cnt = sub_process_init_env(mysql_config, max_retry=3)
    result['init_env_retry'] = retry_cnt

    if not ok:
        result['success'] = False
        result['message'] = f'环境初始化失败，已重试 {retry_cnt} 次，终止整体初始化流程'
        logger.error(result['message'])
        return result

    # —————— 全部通过 ——————
    result['success'] = True
    result['message'] = '初始化流程全部完成'
    logger.info(result['message'])
    return result

