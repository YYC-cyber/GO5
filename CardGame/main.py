#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chronicle of Cards
Web图形界面版 — 运行此文件即可开启 🃏
"""

import os
import signal
import socket
import subprocess
import time


def kill_old_servers():
    """杀掉旧版 Python 服务器进程"""
    killed = 0
    try:
        # 查找占用 5000-5010 端口的进程并杀掉
        for port in range(5000, 5011):
            try:
                result = subprocess.run(
                    ['lsof', '-ti', f':{port}'],
                    capture_output=True, text=True, timeout=3
                )
                if result.stdout.strip():
                    pid = int(result.stdout.strip())
                    os.kill(pid, signal.SIGKILL)
                    killed += 1
                    time.sleep(0.2)
            except (ValueError, ProcessLookupError, OSError):
                pass
            except subprocess.TimeoutExpired:
                pass
    except FileNotFoundError:
        pass  # lsof not available
    return killed


def find_free_port(start=5000, end=5010):
    """找到可用的端口"""
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    return None


if __name__ == "__main__":
    killed = kill_old_servers()
    if killed:
        print(f"🧹 清理了 {killed} 个旧服务器进程")
        time.sleep(0.5)

    port = find_free_port()
    if port is None:
        print("❌ 无法找到可用端口 (5000-5010 均被占用)")
        print("请手动关闭占用端口的程序后重试")
        exit(1)

    from src.web_server import run_server

    try:
        run_server(host='127.0.0.1', port=port, debug=False, open_browser=True)
    except KeyboardInterrupt:
        print("\n\n服务器已停止。再见！")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
