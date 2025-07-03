#!/usr/bin/env python3
"""
德国入籍考试学习助手启动脚本
"""

import subprocess
import sys
import os
import time
import webbrowser
from threading import Thread
from PIL import Image

def install_requirements():
    """安装依赖"""
    print("正在安装Python依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def start_backend():
    """启动后端服务"""
    print("正在启动后端服务...")
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n后端服务已停止")
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")

def start_frontend():
    """启动前端服务"""
    print("正在启动前端服务...")
    time.sleep(3)  # 等待后端启动
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"], check=True)
    except KeyboardInterrupt:
        print("\n前端服务已停止")
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")

def open_browser():
    """打开浏览器"""
    time.sleep(5)  # 等待服务启动
    try:
        webbrowser.open("http://localhost:8501")
        print("🌐 已在浏览器中打开应用")
    except Exception as e:
        print(f"无法自动打开浏览器: {e}")

def main():
    print("🇩🇪 德国入籍考试学习助手")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return
    
    # 安装依赖
    if not install_requirements():
        return
    
    print("\n🚀 启动服务...")
    print("后端API: http://localhost:8000")
    print("前端界面: http://localhost:8501")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    # 启动后端线程
    backend_thread = Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # 启动浏览器线程
    browser_thread = Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # 启动前端
    start_frontend()

if __name__ == "__main__":
    main() 