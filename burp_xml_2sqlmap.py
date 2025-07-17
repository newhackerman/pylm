#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
burp2sqlmap.py
将 BurpSuite 导出的 XML 批量请求转换为 sqlmap 可识别的纯文本格式
用法：
    python burp2sqlmap.py ltgs-urls.txt
输出：
    ltgs-urls_ok.txt
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote_plus

def log(msg):
    print(f"[+] {msg}")

def parse_xml(xml_file):
    """解析 Burp XML，返回 list[bytes] 每个元素是一段完整 HTTP 请求"""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    reqs = []
    for item in root.findall("item"):
        # 基础信息
        host = item.findtext("host", "")
        port = int(item.findtext("port", "80"))
        protocol = item.findtext("protocol", "http").lower()
        method = item.findtext("method", "GET").upper()
        path = item.findtext("path", "/")
        # 原始请求 base64
        request_b64 = item.findtext("request", "")
        if not request_b64:
            continue
        # Burp 的 XML 中 request 是 base64，直接解码即可
        try:
            raw = request_b64.encode("utf-8")
            import base64
            raw = base64.b64decode(raw)
        except Exception:
            continue

        # 如果 raw 里已经包含完整 HTTP 请求（含首行+headers+body），直接保存
        reqs.append(raw)
    return reqs

def normalize_request(raw_bytes):
    """
    保证输出格式与 sqlmap -r 完全一致：
    1. 首行 METHOD PATH HTTP/1.1
    2. 所有 headers
    3. 空行
    4. body（如有）
    5. 末尾无多余换行
    """
    try:
        # 按 \r\n\r\n 或 \n\n 分割 headers/body
        if b"\r\n\r\n" in raw_bytes:
            head, body = raw_bytes.split(b"\r\n\r\n", 1)
        else:
            head, body = raw_bytes.split(b"\n\n", 1)
        lines = head.splitlines()
        # 首行
        first_line = lines[0].decode("utf-8", errors="ignore")
        # 其余 headers
        headers = [line.decode("utf-8", errors="ignore") for line in lines[1:] if line.strip()]
        # 重新拼
        rebuilt = [first_line] + headers + ["", ""]
        rebuilt = "\r\n".join(rebuilt).encode("utf-8") + body
        return rebuilt
    except Exception:
        # 解析失败直接原样返回
        return raw_bytes

def main():
    if len(sys.argv) < 2:
        print("用法: python burp2sqlmap.py <burp_xml_file>")
        sys.exit(1)

    xml_file = Path(sys.argv[1])
    if not xml_file.exists():
        log(f"文件不存在: {xml_file}")
        sys.exit(1)

    out_file = Path("ltgs-urls_ok.txt")
    reqs = parse_xml(xml_file)
    if not reqs:
        log("未解析到任何请求")
        sys.exit(0)

    log(f"共解析到 {len(reqs)} 条请求，写入 {out_file}")
    with open(out_file, "wb") as f:
        for idx, raw in enumerate(reqs, 1):
            normalized = normalize_request(raw)
            f.write(normalized)
            # 每段之间加 ==== 方便 sqlmap 分割
            f.write(b"\r\n====\r\n")

    log("转换完成，可直接用 sqlmap -r ltgs-urls_ok.txt --batch")

if __name__ == "__main__":
    main()