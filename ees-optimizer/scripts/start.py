#!/usr/bin/env python3
"""
储能配置优化系统 - 一键启动脚本
自动完成：端口检测 → 激活虚拟环境 → 启动 Streamlit → 打开浏览器

用法：python start.py [--install-dir <目录>] [--port <端口>]
"""

import os
import sys
import socket
import subprocess
import platform
import time
import webbrowser
import argparse
import signal

DEFAULT_INSTALL_DIR = os.path.expanduser("~/ees-optimizer")
DEFAULT_PORT = 8501
VENV_NAME = ".venv"


def log(msg, level="INFO"):
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERR": "❌", "RUN": "🔧"}
    print(f"  {icons.get(level, '·')}  [{level}] {msg}")


def is_port_available(port):
    """检测端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def find_available_port(start_port, max_attempts=10):
    """找到一个可用端口"""
    for i in range(max_attempts):
        port = start_port + i
        if is_port_available(port):
            return port
    return None


def get_streamlit_cmd(venv_path):
    """获取 streamlit 命令路径"""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "streamlit")
    return os.path.join(venv_path, "bin", "streamlit")


def get_python_cmd(venv_path):
    """获取虚拟环境中 python 的路径"""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "python")
    return os.path.join(venv_path, "bin", "python")


def check_installation(install_dir):
    """检查系统是否已安装"""
    repo_dir = os.path.join(install_dir, "ees-eco-assist-exec-2")
    venv_path = os.path.join(install_dir, VENV_NAME)
    app_py = os.path.join(repo_dir, "app.py")

    if not os.path.exists(app_py):
        log(f"未找到 app.py，请先运行 setup.py 安装系统", "ERR")
        log(f"期望路径: {app_py}", "ERR")
        return None, None

    if not os.path.exists(venv_path):
        log(f"未找到虚拟环境，请先运行 setup.py 安装系统", "ERR")
        return None, None

    return repo_dir, venv_path


def main():
    parser = argparse.ArgumentParser(description="储能配置优化系统 - 一键启动")
    parser.add_argument(
        "--install-dir",
        default=DEFAULT_INSTALL_DIR,
        help=f"安装目录（默认: {DEFAULT_INSTALL_DIR}）",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Streamlit 端口（默认: {DEFAULT_PORT}）",
    )
    args = parser.parse_args()
    install_dir = os.path.abspath(args.install_dir)

    print()
    print("=" * 56)
    print("  ⚡ 储能配置优化系统 · 启动")
    print("=" * 56)
    print()

    # 1. 检查安装
    repo_dir, venv_path = check_installation(install_dir)
    if repo_dir is None:
        sys.exit(1)
    log(f"项目目录: {repo_dir}", "OK")

    # 2. 检测端口
    port = args.port
    if not is_port_available(port):
        log(f"端口 {port} 已被占用，正在寻找可用端口...", "WARN")
        port = find_available_port(port)
        if port is None:
            log("无法找到可用端口，请手动指定: --port <端口号>", "ERR")
            sys.exit(1)
        log(f"已自动切换到端口 {port}", "OK")

    # 3. 启动 Streamlit
    streamlit_cmd = get_streamlit_cmd(venv_path)
    if not os.path.exists(streamlit_cmd):
        # 回退：使用 python -m streamlit
        streamlit_cmd = None
        log("streamlit 命令未找到，尝试使用 python -m streamlit", "WARN")

    url = f"http://localhost:{port}"
    log(f"正在启动 Streamlit 服务 (端口: {port})...", "RUN")

    if streamlit_cmd:
        cmd = [
            streamlit_cmd, "run", "app.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
        ]
    else:
        python_cmd = get_python_cmd(venv_path)
        cmd = [
            python_cmd, "-m", "streamlit", "run", "app.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
        ]

    print()
    print(f"  🌐 访问地址: {url}")
    print(f"  📁 项目目录: {repo_dir}")
    print(f"  按 Ctrl+C 停止服务")
    print()

    # 延迟打开浏览器
    def open_browser():
        time.sleep(3)
        webbrowser.open(url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # 启动 Streamlit（前台运行）
    try:
        proc = subprocess.Popen(cmd, cwd=repo_dir)
        proc.wait()
    except KeyboardInterrupt:
        print()
        log("正在停止服务...", "RUN")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        log("服务已停止", "OK")
    except Exception as e:
        log(f"启动失败: {e}", "ERR")
        sys.exit(1)


if __name__ == "__main__":
    main()
