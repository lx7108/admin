# H-Pulse·Mirage 一键部署脚本
# 作者: AI Assistant
# 日期: 2025-03-27

# 检查是否安装了Docker
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerInstalled) {
    Write-Error "未检测到Docker，请先安装Docker和Docker Compose。"
    exit 1
}

# 确认Docker正在运行
try {
    docker info | Out-Null
} catch {
    Write-Error "Docker似乎没有正常运行。请确保Docker服务已启动。"
    exit 1
}

# 创建环境变量文件
$env:SECRET_KEY = [Guid]::NewGuid().ToString()
$envContent = @"
DATABASE_URL=postgresql://postgres:postgres@db:5432/h_pulse_mirage
SECRET_KEY=$($env:SECRET_KEY)
DEBUG=False
STORAGE_PATH=/app/storage
"@

# 保存环境变量到.env文件
Set-Content -Path "$PSScriptRoot/h_pulse_mirage/.env" -Value $envContent

Write-Host "=== H-Pulse·Mirage 部署开始 ===" -ForegroundColor Cyan
Write-Host "环境配置完成，秘钥已自动生成" -ForegroundColor Green

# 切换到项目目录
Set-Location -Path "$PSScriptRoot/h_pulse_mirage"

# 拉取所需的Docker镜像
Write-Host "正在拉取所需Docker镜像..." -ForegroundColor Yellow
docker-compose pull

# 构建和启动服务
Write-Host "正在构建和启动服务..." -ForegroundColor Yellow
docker-compose up -d --build

# 等待服务启动
Write-Host "正在等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查服务是否启动成功
$apiStatus = curl -s -o /null -w "%{http_code}" http://localhost:8000 2>$null
if ($apiStatus -eq 200) {
    Write-Host "API服务启动成功!" -ForegroundColor Green
} else {
    Write-Host "API服务可能未正常启动，请检查容器日志。" -ForegroundColor Red
    Write-Host "可使用命令: docker-compose logs -f api" -ForegroundColor Yellow
}

# 输出访问信息
Write-Host "=== H-Pulse·Mirage 部署完成 ===" -ForegroundColor Cyan
Write-Host "您可以通过以下地址访问服务:" -ForegroundColor Green
Write-Host "API服务:      http://localhost:8000" -ForegroundColor White
Write-Host "API文档:      http://localhost:8000/docs" -ForegroundColor White
Write-Host "Grafana监控:  http://localhost:3000 (默认用户名/密码: admin/admin)" -ForegroundColor White
Write-Host "Prometheus:   http://localhost:9090" -ForegroundColor White

# 提示如何停止服务
Write-Host "`n如需停止服务，请运行:" -ForegroundColor Yellow
Write-Host "cd $PSScriptRoot/h_pulse_mirage && docker-compose down" -ForegroundColor White 