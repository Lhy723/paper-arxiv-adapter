#!/usr/bin/env python3
"""开发服务器启动脚本 - 同时启动前后端"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    project_root = Path(__file__).parent
    backend_dir = project_root / "web" / "backend"
    frontend_dir = project_root / "web" / "frontend"
    
    print("🚀 启动 ArXiv Paper Adapter 开发服务器...")
    print("-" * 50)
    
    # 启动后端
    print("📦 启动后端服务器 (端口 8000)...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"],
        cwd=backend_dir,
    )
    
    # 启动前端
    print("🎨 启动前端开发服务器 (端口 5173)...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=True,
    )
    
    print("-" * 50)
    print("✅ 开发服务器已启动！")
    print("   前端: http://localhost:5173")
    print("   后端: http://localhost:8000")
    print("   API文档: http://localhost:8000/docs")
    print("-" * 50)
    print("按 Ctrl+C 停止所有服务...")
    
    try:
        # 等待进程结束
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()
