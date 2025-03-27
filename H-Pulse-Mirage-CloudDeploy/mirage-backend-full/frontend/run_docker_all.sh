#!/bin/bash
echo "使用 Docker 启动 H-Pulse 前后端系统..."

# 进入前端目录（包含 docker-compose 和 nginx 配置）
cd /mnt/data/h_pulse_frontend

# 启动所有服务
docker-compose up --build
