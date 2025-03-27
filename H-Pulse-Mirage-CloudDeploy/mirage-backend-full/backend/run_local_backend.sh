#!/bin/bash
echo "正在启动 H-Pulse 后端（本地开发模式）..."

# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py
python seed_data.py

# 启动 FastAPI 应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
