import json
import os
import time
import requests
import subprocess
import logging
import sys
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sqlmap_batch.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 配置
SQLMAP_API_PATH = r"C:\Users\test\Desktop\sqlmap\sqlmapapi.py"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8775
URLS_FILE = "ltgs-urls.txt"
HEADERS_FILE = "headers.json"
RESULTS_FILE = "injection_results.txt"
MAX_RETRIES = 3
TIMEOUT = 30  # 超时时间(秒)

def start_sqlmap_api():
    """启动sqlmapapi服务"""
    try:
        logger.info("正在启动sqlmapapi服务...")
        process = subprocess.Popen(["python", SQLMAP_API_PATH, "-s", SERVER_HOST, "-p", str(SERVER_PORT)],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)  # 等待服务启动
        return process
    except Exception as e:
        logger.error(f"启动sqlmapapi服务失败: {e}")
        return None

def check_api_status():
    """检查sqlmapapi服务是否在运行"""
    try:
        response = requests.get(f"http://{SERVER_HOST}:{SERVER_PORT}/", timeout=TIMEOUT)
        return response.status_code == 200
    except:
        return False

def create_new_task():
    """创建新的扫描任务"""
    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(f"http://{SERVER_HOST}:{SERVER_PORT}/task/new", timeout=TIMEOUT)
            if response.status_code == 200:
                task_data = response.json()
                if task_data["success"]:
                    return task_data["taskid"]
            time.sleep(1)
        except Exception as e:
            logger.error(f"创建任务失败: {e}")
            time.sleep(2)
    return None

def delete_task(task_id):
    """删除任务"""
    try:
        requests.get(f"http://{SERVER_HOST}:{SERVER_PORT}/task/{task_id}/delete", timeout=TIMEOUT)
    except:
        pass

def start_scan(task_id, url, headers):
    """开始扫描"""
    options = {
        "url": url,
        "headers": headers,
        "level": 1,
        "risk": 1,
        "threads": 3,
        "timeout": 300,
        "retries": 3,
        "randomAgent": True,
        "batch": True,
        "getDbs": True,
        "getTables": True,
        "smart": True,
        "testParameter": None,  # 自动检测参数
    }
    
    for _ in range(MAX_RETRIES):
        try:
            response = requests.post(
                f"http://{SERVER_HOST}:{SERVER_PORT}/scan/{task_id}/start",
                json=options,
                timeout=TIMEOUT
            )
            json_data = response.json()
            if json_data["success"]:
                return True
        except Exception as e:
            logger.error(f"启动扫描失败: {e}")
            time.sleep(2)
    return False

def get_scan_status(task_id):
    """获取扫描状态"""
    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(
                f"http://{SERVER_HOST}:{SERVER_PORT}/scan/{task_id}/status",
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            logger.error(f"获取扫描状态失败: {e}")
            time.sleep(2)
    return {"status": "unknown"}

def get_scan_data(task_id):
    """获取扫描结果数据"""
    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(
                f"http://{SERVER_HOST}:{SERVER_PORT}/scan/{task_id}/data",
                timeout=TIMEOUT
            )
            return response.json()
        except Exception as e:
            logger.error(f"获取扫描数据失败: {e}")
            time.sleep(2)
    return {"data": []}

def extract_vulnerable_info(data):
    """提取注入点信息和数据库信息"""
    result = {
        "vulnerable": False,
        "parameter": "",
        "place": "",
        "payload": "",
        "databases": [],
        "tables": {}
    }
    
    if not data or "data" not in data or not data["data"]:
        return result
    
    for item in data["data"]:
        # 检查是否存在注入点
        if "type" in item and item["type"] == 1:  # type 1表示注入点
            if "value" in item:
                result["vulnerable"] = True
                for detail in item["value"]:
                    if "parameter" in detail:
                        result["parameter"] = detail.get("parameter", "")
                    if "place" in detail:
                        result["place"] = detail.get("place", "")
                    if "payload" in detail:
                        result["payload"] = detail.get("payload", "")
        
        # 提取数据库信息
        if "type" in item and item["type"] == 2:  # type 2表示数据库信息
            if "value" in item and isinstance(item["value"], list):
                result["databases"] = item["value"]
        
        # 提取表信息
        if "type" in item and item["type"] == 3:  # type 3表示表信息
            if "value" in item and isinstance(item["value"], dict):
                result["tables"] = item["value"]
    
    return result

def process_url(url, headers):
    """处理单个URL"""
    logger.info(f"开始处理URL: {url}")
    
    task_id = create_new_task()
    if not task_id:
        logger.error(f"为URL创建任务失败: {url}")
        return None
    
    logger.info(f"已创建任务ID: {task_id} 用于URL: {url}")
    
    # 开始扫描
    if not start_scan(task_id, url, headers):
        logger.error(f"启动扫描失败, 任务ID: {task_id}, URL: {url}")
        delete_task(task_id)
        return None
    
    logger.info(f"已启动扫描, 任务ID: {task_id}, URL: {url}")
    
    # 等待扫描完成
    while True:
        status_data = get_scan_status(task_id)
        if status_data.get("status") == "terminated":
            logger.info(f"扫描已完成, 任务ID: {task_id}, URL: {url}")
            break
        elif status_data.get("status") == "running":
            logger.info(f"扫描中... 任务ID: {task_id}, URL: {url}")
            time.sleep(10)
        else:
            logger.warning(f"未知状态: {status_data.get('status')}, 任务ID: {task_id}, URL: {url}")
            time.sleep(5)
    
    # 获取扫描结果
    scan_data = get_scan_data(task_id)
    result = extract_vulnerable_info(scan_data)
    
    # 删除任务
    delete_task(task_id)
    
    if result["vulnerable"]:
        logger.info(f"发现注入点! URL: {url}, 参数: {result['parameter']}")
        return {
            "url": url,
            "parameter": result["parameter"],
            "place": result["place"],
            "payload": result["payload"],
            "databases": result["databases"],
            "tables": result["tables"]
        }
    else:
        logger.info(f"URL未发现注入点: {url}")
        return None

def load_headers():
    """从文件加载请求头"""
    try:
        with open(HEADERS_FILE, 'r', encoding='utf-8') as f:
            headers_data = json.load(f)
        
        # 如果headers是字符串，尝试解析
        if isinstance(headers_data, str):
            return json.loads(headers_data)
        return headers_data
    except Exception as e:
        logger.error(f"加载headers失败: {e}")
        return {}

def load_urls():
    """从文件加载URL列表"""
    try:
        with open(URLS_FILE, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f.readlines() if line.strip()]
        return urls
    except Exception as e:
        logger.error(f"加载URL列表失败: {e}")
        return []

def save_results(results):
    """保存注入结果到文件"""
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        f.write("SQL注入扫描结果\n")
        f.write("=" * 80 + "\n\n")
        
        if not results:
            f.write("未发现注入点\n")
            return
        
        for i, result in enumerate(results, 1):
            f.write(f"[漏洞 #{i}]\n")
            f.write(f"URL: {result['url']}\n")
            f.write(f"参数: {result['parameter']}\n")
            f.write(f"位置: {result['place']}\n")
            f.write(f"Payload: {result['payload']}\n")
            
            f.write("\n数据库列表:\n")
            for db in result['databases']:
                f.write(f"- {db}\n")
            
            f.write("\n表信息:\n")
            for db, tables in result['tables'].items():
                f.write(f"数据库 '{db}' 中的表:\n")
                for table in tables:
                    f.write(f"  - {table}\n")
            
            f.write("\n" + "=" * 80 + "\n\n")

def main():
    """主函数"""
    logger.info("开始批量SQL注入扫描")
    
    # 加载URL和headers
    urls = load_urls()
    headers = load_headers()
    
    if not urls:
        logger.error("URL列表为空,无法继续")
        return
    
    logger.info(f"已加载 {len(urls)} 个URL")
    
    # 启动sqlmapapi服务
    api_process = None
    if not check_api_status():
        api_process = start_sqlmap_api()
        if not api_process:
            logger.error("无法启动sqlmapapi服务,退出")
            return
    
    # 存储结果
    results = []
    
    try:
        # 处理每个URL
        for i, url in enumerate(urls, 1):
            logger.info(f"处理URL [{i}/{len(urls)}]: {url}")
            
            # 检查API服务是否正常
            if not check_api_status():
                logger.warning("sqlmapapi服务不可用,尝试重启...")
                if api_process:
                    try:
                        api_process.terminate()
                        time.sleep(2)
                    except:
                        pass
                api_process = start_sqlmap_api()
                if not api_process:
                    logger.error("重启sqlmapapi服务失败,跳过当前URL")
                    continue
                logger.info("sqlmapapi服务已重启")
            
            # 处理URL
            result = process_url(url, headers)
            if result:
                results.append(result)
    
    except KeyboardInterrupt:
        logger.info("用户中断执行")
    except Exception as e:
        logger.error(f"执行过程中发生错误: {e}")
    finally:
        # 保存结果
        save_results(results)
        logger.info(f"扫描结果已保存至 {RESULTS_FILE}")
        
        # 关闭sqlmapapi服务
        if api_process:
            logger.info("关闭sqlmapapi服务")
            api_process.terminate()
    
    logger.info(f"扫描完成,共发现 {len(results)} 个注入点")

if __name__ == "__main__":
    main()