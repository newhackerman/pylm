#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量调用 sqlmapapi，对 burp2sqlmap.py 生成的 ltgs-urls_ok.txt 进行注入检测
1. 读取完整 HTTP 报文（含 headers/cookies/body）
2. 逐段提交给 sqlmapapi
3. 发现注入后记录 url、参数、dbs、tables
4. 全程无人值守：超时保护、sqlmapapi 断线自动重启
用法：
    python batch_sqlmapapi.py ltgs-urls_ok.txt
"""

import os
import sys
import json
import time
import signal
import subprocess
import requests
from pathlib import Path

# ========== 全局配置 ==========
SQLMAP_DIR = Path(r"C:\Users\test\Desktop\sqlmap")
SQLMAPAPI_PY = SQLMAP_DIR / "sqlmapapi.py"
RESULT_FILE = Path("injection_result.txt")

API_HOST = "127.0.0.1"
API_PORT = 8775
API_BASE = f"http://{API_HOST}:{API_PORT}"

TASK_TIMEOUT = 300          # 单个任务最大运行时间（秒）
POLL_INTERVAL = 3
API_START_MAX_WAIT = 30
# ==============================

# ---------- 工具函数 ----------
def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def kill_proc(proc):
    if proc and proc.poll() is None:
        proc.send_signal(signal.CTRL_BREAK_EVENT if os.name == 'nt' else signal.SIGTERM)
        proc.wait()

def start_sqlmapapi():
    cmd = [sys.executable, str(SQLMAPAPI_PY), "-s", "-H", API_HOST, "-p", str(API_PORT)]
    proc = subprocess.Popen(cmd, cwd=str(SQLMAP_DIR),
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
    for _ in range(API_START_MAX_WAIT):
        try:
            if requests.get(f"{API_BASE}/admin/0/list", timeout=5).status_code == 200:
                log("sqlmapapi 已就绪")
                return proc
        except requests.RequestException:
            pass
        time.sleep(1)
    log("sqlmapapi 启动失败")
    kill_proc(proc)
    return None

def restart_sqlmapapi(proc):
    log("检测到 sqlmapapi 异常，准备重启...")
    kill_proc(proc)
    return start_sqlmapapi()

def read_requests(file_path):
    """读取 burp2sqlmap 生成的文件，按 ==== 分割成 list[bytes]"""
    raw = Path(file_path).read_bytes()
    blocks = raw.split(b"\r\n====\r\n")
    # 去掉空块
    return [b for b in blocks if b.strip()]

def new_task():
    r = requests.get(f"{API_BASE}/task/new")
    if r.status_code == 200 and r.json().get("success"):
        return r.json()["taskid"]
    return None

def delete_task(taskid):
    requests.get(f"{API_BASE}/task/{taskid}/delete")

def start_scan(taskid, raw_http):
    """把完整 HTTP 报文直接发给 sqlmapapi"""
    files = {"request": ("req.txt", raw_http, "application/octet-stream")}
    data = {
        "level": 2,
        "risk": 2,
        "getDbs": True,
        "getTables": True,
        "threads": 4,
        "timeout": TASK_TIMEOUT
    }
    r = requests.post(f"{API_BASE}/scan/{taskid}/start", data=data, files=files, timeout=10)
    return r.status_code == 200 and r.json().get("success")

def wait_task(taskid):
    start = time.time()
    while time.time() - start < TASK_TIMEOUT:
        try:
            r = requests.get(f"{API_BASE}/scan/{taskid}/status", timeout=5)
            if r.status_code != 200:
                return "error"
            status = r.json()["status"]
            if status in ("terminated", "finished"):
                return "done"
            if status == "running":
                time.sleep(POLL_INTERVAL)
                continue
            return "error"
        except requests.RequestException:
            return "error"
    return "timeout"

def get_injection_summary(taskid):
    try:
        data = requests.get(f"{API_BASE}/scan/{taskid}/data", timeout=10).json()
        if not data.get("data"):
            return None
        # 取第一条注入记录
        inj = data["data"][0]
        url = inj.get("value", {}).get("url", "")
        parameter = inj.get("value", {}).get("parameter", "")
        dbs, tables = [], []
        for item in data.get("data", []):
            if item.get("type") == 1:
                dbs = item.get("value", [])
            elif item.get("type") == 2:
                tables = item.get("value", [])
        return {"url": url, "parameter": parameter, "dbs": dbs, "tables": tables}
    except Exception:
        return None

def save_result(summary):
    with open(RESULT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")

# ---------- 主流程 ----------
def main():
    if len(sys.argv) < 2:
        print("用法: python batch_sqlmapapi.py <ltgs-urls_ok.txt>")
        sys.exit(1)

    req_file = Path(sys.argv[1])
    if not req_file.exists():
        log(f"{req_file} 不存在")
        sys.exit(1)

    requests_list = read_requests(req_file)
    if not requests_list:
        log("未读取到任何请求")
        return

    log(f"共 {len(requests_list)} 条请求，开始检测...")

    api_proc = start_sqlmapapi()
    if not api_proc:
        log("sqlmapapi 启动失败，脚本终止")
        return

    try:
        for idx, raw in enumerate(requests_list, 1):
            log(f"[{idx}/{len(requests_list)}] 检测第 {idx} 条请求")
            taskid = new_task()
            if not taskid:
                log("创建任务失败，尝试重启 api")
                api_proc = restart_sqlmapapi(api_proc)
                continue

            if not start_scan(taskid, raw):
                log("下发任务失败，跳过")
                delete_task(taskid)
                continue

            status = wait_task(taskid)
            if status == "done":
                summary = get_injection_summary(taskid)
                if summary:
                    log("发现注入！记录结果")
                    save_result(summary)
                else:
                    log("未检测到注入")
            elif status == "timeout":
                log("任务超时")
            else:
                log("任务异常，尝试重启 api")
                api_proc = restart_sqlmapapi(api_proc)

            delete_task(taskid)
    finally:
        kill_proc(api_proc)
        log("全部完成")

if __name__ == "__main__":
    main()