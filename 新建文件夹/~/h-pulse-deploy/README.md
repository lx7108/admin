# H-Pulse·Mirage 一键部署指南

这是H-Pulse·Mirage命运模拟与演出引擎的一键部署包。本指南将帮助您快速部署系统。

## 系统要求

- Docker 19.03+
- Docker Compose 1.27+
- 至少2GB RAM
- 至少10GB可用磁盘空间

## 部署步骤

### Windows系统

1. 确保已安装Docker Desktop并启动
2. 打开PowerShell终端
3. 运行部署脚本：
   ```powershell
   cd h-pulse-deploy
   .\deploy.ps1
   ```

### Linux/macOS系统

1. 确保已安装Docker和Docker Compose
2. 打开终端
3. 为脚本添加执行权限并运行：
   ```bash
   cd h-pulse-deploy
   chmod +x deploy.sh
   ./deploy.sh
   ```

## 验证部署

成功部署后，您可以通过以下地址访问服务：

- API服务: http://localhost:8000
- API文档: http://localhost:8000/docs
- Grafana监控: http://localhost:3000 (默认用户名/密码: admin/admin)
- Prometheus: http://localhost:9090

## 默认账户

系统会自动创建以下默认账户：
- 管理员账户: admin/admin

## 停止服务

要停止所有服务，请运行：

```bash
cd h-pulse-deploy/h_pulse_mirage
docker-compose down
```

要完全删除所有数据（包括数据库和卷），请运行：

```bash
cd h-pulse-deploy/h_pulse_mirage
docker-compose down -v
```

## 常见问题

1. **端口冲突**：如果遇到端口冲突，请修改docker-compose.yml文件中的端口映射。

2. **数据库连接失败**：检查.env文件中的数据库连接信息是否正确。

3. **服务未启动**：运行`docker-compose logs -f api`查看API服务日志。

4. **修改默认配置**：部署后，可以修改.env文件中的配置，然后重启服务：
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## 生产环境注意事项

1. 修改.env文件中的密码和密钥
2. 配置HTTPS
3. 配置防火墙规则
4. 设置数据备份

## 支持与帮助

如需更多帮助，请参考项目文档或提交Issue。 