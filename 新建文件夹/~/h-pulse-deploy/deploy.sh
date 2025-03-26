#!/bin/bash

# H-Pulse·Mirage 一键部署脚本
# 作者: AI Assistant
# 日期: 2025-03-27

set -e  # 遇到错误时停止执行

# 检查是否安装了Docker
if ! command -v docker &> /dev/null; then
    echo "错误: 未检测到Docker，请先安装Docker和Docker Compose。"
    exit 1
fi

# 检查是否安装了Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "错误: 未检测到Docker Compose，请先安装。"
    exit 1
fi

# 确认Docker正在运行
if ! docker info &> /dev/null; then
    echo "错误: Docker似乎没有正常运行。请确保Docker服务已启动。"
    exit 1
fi

# 创建环境变量文件
SECRET_KEY=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
cat > "$(dirname "$0")/h_pulse_mirage/.env" << EOF
DATABASE_URL=postgresql://postgres:postgres@db:5432/h_pulse_mirage
SECRET_KEY=${SECRET_KEY}
DEBUG=False
STORAGE_PATH=/app/storage
EOF

echo -e "\e[36m=== H-Pulse·Mirage 部署开始 ===\e[0m"
echo -e "\e[32m环境配置完成，秘钥已自动生成\e[0m"

# 切换到项目目录
cd "$(dirname "$0")/h_pulse_mirage"

# 确保存储目录存在并设置权限
mkdir -p storage
chmod -R 777 storage

# 拉取所需的Docker镜像
echo -e "\e[33m正在拉取所需Docker镜像...\e[0m"
docker-compose pull

# 构建和启动服务
echo -e "\e[33m正在构建和启动服务...\e[0m"
docker-compose up -d --build

# 等待服务启动
echo -e "\e[33m正在等待服务启动...\e[0m"
sleep 10

# 检查服务是否启动成功
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000; then
    echo -e "\e[32mAPI服务启动成功!\e[0m"
else
    echo -e "\e[31mAPI服务可能未正常启动，请检查容器日志。\e[0m"
    echo -e "\e[33m可使用命令: docker-compose logs -f api\e[0m"
fi

# 输出访问信息
echo -e "\e[36m=== H-Pulse·Mirage 部署完成 ===\e[0m"
echo -e "\e[32m您可以通过以下地址访问服务:\e[0m"
echo -e "API服务:      http://localhost:8000"
echo -e "API文档:      http://localhost:8000/docs"
echo -e "Grafana监控:  http://localhost:3000 (默认用户名/密码: admin/admin)"
echo -e "Prometheus:   http://localhost:9090"

# 提示如何停止服务
echo -e "\n\e[33m如需停止服务，请运行:\e[0m"
echo -e "cd $(pwd) && docker-compose down" 