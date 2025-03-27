#!/bin/bash

echo "🚀 正在初始化云服务器环境..."

# 安装 Docker
if ! command -v docker &> /dev/null
then
    echo "📦 安装 Docker..."
    curl -fsSL https://get.docker.com | bash
fi

# 安装 Docker Compose
if ! command -v docker-compose &> /dev/null
then
    echo "📦 安装 Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 解压部署包（假设已上传）
DEPLOY_DIR="H-Pulse-Mirage-CloudDeploy"
cd ~
unzip $DEPLOY_DIR.zip -d $DEPLOY_DIR

# 启动服务
cd $DEPLOY_DIR
docker compose up --build -d

echo "✅ 部署完成！前端: http://服务器IP:4173，后端: http://服务器IP:8000"