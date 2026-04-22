#!/usr/bin/env python3
"""
储能配置优化系统 - 一键部署脚本
自动完成：环境检测 → 创建虚拟环境 → 安装依赖 → 克隆代码

用法：python setup.py [--install-dir <目录>]
默认安装到 ~/ees-optimizer/
"""

import os
import sys
import subprocess
import shutil
import argparse
import platform

# ── 配置 ──
REPO_URL = "https://gitee.com/xess531/ees-eco-assist-exec-2.git"
DEFAULT_INSTALL_DIR = os.path.expanduser("~/ees-optimizer")
VENV_NAME = ".venv"
MIN_PYTHON = (3, 9)

REQUIREMENTS = [
    "numpy",
    "pandas",
    "streamlit",
    "plotly",
    "pyomo",
    "highspy",
    "networkx",
    "cloudpickle",
    "tqdm",
    "matplotlib",
    "requests",
    "pytz",
    "openpyxl",
]


def log(msg, level="INFO"):
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERR": "❌", "RUN": "🔧"}
    print(f"  {icons.get(level, '·')}  [{level}] {msg}")


def run_cmd(cmd, cwd=None, check=True):
    """运行命令并返回结果"""
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, shell=isinstance(cmd, str)
    )
    if check and result.returncode != 0:
        log(f"命令失败: {cmd}", "ERR")
        if result.stderr:
            log(f"错误信息: {result.stderr.strip()}", "ERR")
        return None
    return result


def check_python():
    """检测 Python 版本"""
    ver = sys.version_info
    log(f"Python 版本: {ver.major}.{ver.minor}.{ver.micro}")
    if (ver.major, ver.minor) < MIN_PYTHON:
        log(f"需要 Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+，当前为 {ver.major}.{ver.minor}", "ERR")
        log("请安装 Python 3.9 或更高版本: https://www.python.org/downloads/", "ERR")
        return False
    log("Python 版本满足要求", "OK")
    return True


def check_pip():
    """检测 pip 可用性"""
    result = run_cmd([sys.executable, "-m", "pip", "--version"], check=False)
    if result and result.returncode == 0:
        log("pip 可用", "OK")
        return True
    log("pip 不可用，请先安装 pip", "ERR")
    return False


def check_venv():
    """检测 venv 模块可用性"""
    result = run_cmd([sys.executable, "-c", "import venv"], check=False)
    if result and result.returncode == 0:
        log("venv 模块可用", "OK")
        return True
    log("venv 模块不可用", "ERR")
    if platform.system() == "Linux":
        log("在 Ubuntu/Debian 上请运行: sudo apt install python3-venv", "WARN")
    return False


def check_git():
    """检测 git 可用性"""
    result = run_cmd(["git", "--version"], check=False)
    if result and result.returncode == 0:
        log(f"Git: {result.stdout.strip()}", "OK")
        return True
    log("Git 未安装", "ERR")
    log("请安装 Git: https://git-scm.com/downloads", "ERR")
    return False


def check_already_installed(install_dir):
    """检测是否已安装"""
    app_py = os.path.join(install_dir, "ees-eco-assist-exec-2", "app.py")
    venv_dir = os.path.join(install_dir, VENV_NAME)
    if os.path.exists(app_py) and os.path.exists(venv_dir):
        log("系统已安装，跳过重复安装", "OK")
        return True
    return False


def create_venv(install_dir):
    """创建虚拟环境"""
    venv_path = os.path.join(install_dir, VENV_NAME)
    if os.path.exists(venv_path):
        log("虚拟环境已存在，跳过创建", "OK")
        return venv_path

    log("正在创建虚拟环境...", "RUN")
    result = run_cmd([sys.executable, "-m", "venv", venv_path])
    if result is None:
        return None
    log("虚拟环境创建完成", "OK")
    return venv_path


def get_pip_cmd(venv_path):
    """获取虚拟环境中 pip 的路径"""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "pip")
    return os.path.join(venv_path, "bin", "pip")


def get_python_cmd(venv_path):
    """获取虚拟环境中 python 的路径"""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "python")
    return os.path.join(venv_path, "bin", "python")


def install_deps(venv_path):
    """安装依赖"""
    pip_cmd = get_pip_cmd(venv_path)

    # 先升级 pip
    log("正在升级 pip...", "RUN")
    run_cmd([pip_cmd, "install", "--upgrade", "pip"], check=False)

    # 安装依赖
    total = len(REQUIREMENTS)
    for i, pkg in enumerate(REQUIREMENTS, 1):
        log(f"正在安装 [{i}/{total}]: {pkg}", "RUN")
        result = run_cmd([pip_cmd, "install", pkg], check=False)
        if result and result.returncode == 0:
            log(f"{pkg} 安装完成", "OK")
        else:
            log(f"{pkg} 安装失败，请稍后手动安装: {pip_cmd} install {pkg}", "WARN")

    log("所有依赖安装完成", "OK")


def clone_repo(install_dir):
    """克隆代码仓库"""
    repo_dir = os.path.join(install_dir, "ees-eco-assist-exec-2")
    if os.path.exists(repo_dir):
        log("代码仓库已存在，尝试更新...", "RUN")
        result = run_cmd(["git", "pull"], cwd=repo_dir, check=False)
        if result and result.returncode == 0:
            log("代码已更新到最新版本", "OK")
        else:
            log("代码更新失败，使用现有版本", "WARN")
        return repo_dir

    log(f"正在从 Gitee 克隆代码...", "RUN")
    result = run_cmd(["git", "clone", REPO_URL], cwd=install_dir)
    if result is None:
        log("代码克隆失败，请检查网络连接", "ERR")
        return None
    log("代码克隆完成", "OK")
    return repo_dir


def verify_installation(install_dir, venv_path):
    """验证安装是否成功"""
    python_cmd = get_python_cmd(venv_path)
    repo_dir = os.path.join(install_dir, "ees-eco-assist-exec-2")

    log("正在验证安装...", "RUN")

    # 检查关键文件
    for f in ["app.py", "engine.py", "Data/LMP_data.xlsx"]:
        path = os.path.join(repo_dir, f)
        if not os.path.exists(path):
            log(f"缺少文件: {f}", "ERR")
            return False

    # 检查关键包是否可导入
    test_imports = "import numpy, pandas, streamlit, plotly, pyomo"
    result = run_cmd([python_cmd, "-c", test_imports], check=False)
    if result and result.returncode == 0:
        log("核心依赖导入成功", "OK")
    else:
        log("部分依赖导入失败，但不影响安装完成", "WARN")

    # 检查 HiGHS 求解器
    test_highs = "import highspy; print('HiGHS OK')"
    result = run_cmd([python_cmd, "-c", test_highs], check=False)
    if result and result.returncode == 0:
        log("HiGHS 求解器可用", "OK")
    else:
        log("HiGHS 求解器未安装，优化计算可能无法运行", "WARN")

    return True


def main():
    parser = argparse.ArgumentParser(description="储能配置优化系统 - 一键部署")
    parser.add_argument(
        "--install-dir",
        default=DEFAULT_INSTALL_DIR,
        help=f"安装目录（默认: {DEFAULT_INSTALL_DIR}）",
    )
    args = parser.parse_args()
    install_dir = os.path.abspath(args.install_dir)

    print()
    print("=" * 56)
    print("  ⚡ 储能配置优化系统 · 一键部署")
    print("=" * 56)
    print(f"  安装目录: {install_dir}")
    print(f"  操作系统: {platform.system()} {platform.machine()}")
    print()

    # 1. 环境检测
    print("── 步骤 1/5: 环境检测 ──")
    ok = check_python() and check_pip() and check_venv() and check_git()
    if not ok:
        log("环境检测未通过，请修复上述问题后重试", "ERR")
        sys.exit(1)
    print()

    # 2. 检查是否已安装
    print("── 步骤 2/5: 检查已有安装 ──")
    if check_already_installed(install_dir):
        print()
        print("── 安装已完成 ──")
        print(f"  项目目录: {install_dir}/ees-eco-assist-exec-2")
        print()
        sys.exit(0)
    print()

    # 3. 创建安装目录和虚拟环境
    print("── 步骤 3/5: 创建虚拟环境 ──")
    os.makedirs(install_dir, exist_ok=True)
    venv_path = create_venv(install_dir)
    if venv_path is None:
        log("虚拟环境创建失败", "ERR")
        sys.exit(1)
    print()

    # 4. 安装依赖
    print("── 步骤 4/5: 安装依赖 ──")
    install_deps(venv_path)
    print()

    # 5. 克隆代码
    print("── 步骤 5/5: 克隆代码 ──")
    repo_dir = clone_repo(install_dir)
    if repo_dir is None:
        sys.exit(1)
    print()

    # 验证
    print("── 验证安装 ──")
    if verify_installation(install_dir, venv_path):
        log("安装验证通过！", "OK")
    else:
        log("安装验证有警告，但基本结构完整", "WARN")

    print()
    print("=" * 56)
    print("  ✅ 部署完成！")
    print("=" * 56)
    print(f"  📁 安装目录:   {install_dir}")
    print(f"  📁 项目代码:   {install_dir}/ees-eco-assist-exec-2")
    print(f"  📁 虚拟环境:   {venv_path}")
    print()
    sys.exit(0)


if __name__ == "__main__":
    main()
