# H-Pulse·Mirage

命运模拟与演出引擎 - 基于命理系统与AI行为模拟的虚拟人生体验平台

## 项目简介

H-Pulse·Mirage是一个创新性的命运模拟与演出引擎，融合了命理学、人工智能、行为心理学和因果推理，为用户提供一个可以体验不同人生轨迹的虚拟现实平台。

核心功能：
- 基于出生信息的八字命盘生成与五行分析
- 人格特质与情绪状态模拟
- AI驱动的决策行为模拟（基于PPO强化学习）
- 命运事件因果链追踪与可视化
- 命运剧场演出与台词生成
- 角色对抗互动模拟
- 命运NFT生成与收藏系统

## 系统架构

![系统架构](https://github.com/your-repo/h-pulse-mirage/raw/main/docs/assets/architecture.png)

### 核心模块

1. **命理引擎**
   - 八字排盘系统
   - 五行属性分析器
   - 命运评分模型

2. **AI行为引擎**
   - PPO强化学习模型
   - 角色行为模拟环境
   - 决策矩阵生成器

3. **因果推理系统**
   - 事件因果图构建
   - 命运路径分析
   - 可能性分支预测

4. **NFT生成系统**
   - 命运剧本生成
   - 剧场演出引擎
   - NFT市场与交易

## 技术栈

- **后端**：FastAPI + SQLAlchemy + PostgreSQL
- **AI模块**：PyTorch + OpenAI Gym
- **前端**：Vue.js 3 + D3.js（可视化）
- **监控**：Prometheus + Grafana
- **容器化**：Docker + Docker Compose

## 快速开始

### 环境要求
- Python 3.9+
- PostgreSQL 12+
- Docker & Docker Compose (可选)
- Node.js 14+ (前端开发)

### 使用Docker运行

1. 克隆仓库
```bash
git clone https://github.com/your-repo/h-pulse-mirage.git
cd h-pulse-mirage
```

2. 使用Docker Compose启动服务
```bash
docker-compose up -d
```

3. 访问应用
   - API服务: http://localhost:8000
   - API文档: http://localhost:8000/docs
   - Grafana监控: http://localhost:3000

### 本地开发环境

1. 克隆仓库
```bash
git clone https://github.com/your-repo/h-pulse-mirage.git
cd h-pulse-mirage
```

2. 安装Python依赖
```bash
pip install -r requirements.txt
```

3. 配置数据库
   - 创建.env文件并设置数据库连接信息
   ```
   DATABASE_URL=postgresql://postgres:password@localhost:5432/h_pulse_mirage
   SECRET_KEY=your_secret_key
   DEBUG=True
   ```

4. 初始化数据库
```bash
alembic upgrade head
```

5. 启动服务
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 项目结构

```
h_pulse_mirage/
├── alembic/                # 数据库迁移管理
├── app/                    # 应用主目录
│   ├── core/               # 核心模块
│   │   ├── bazi_engine.py  # 八字分析引擎
│   │   ├── fate_engine.py  # 命运评分引擎
│   │   ├── ppo_agent.py    # PPO智能体实现
│   │   └── security.py     # 安全认证模块
│   ├── engine/             # 引擎模块
│   │   ├── causal_graph.py # 因果图构建
│   │   └── drama_builder.py # 剧场生成器
│   ├── middleware/         # 中间件
│   │   └── logger.py       # 日志中间件
│   ├── models/             # 数据模型
│   │   ├── character.py    # 角色模型
│   │   ├── destiny.py      # 命运事件模型
│   │   ├── fate_nft.py     # 命运NFT模型
│   │   └── ...
│   ├── monitoring/         # 监控模块
│   │   └── metrics.py      # 指标收集器
│   ├── pvp_arena/          # 对抗系统
│   │   └── arena_engine.py # 对抗引擎
│   ├── routers/            # API路由
│   │   ├── character_router.py 
│   │   ├── destiny_router.py
│   │   └── ...
│   ├── schemas/            # 数据验证模型
│   │   ├── character_schema.py
│   │   └── ...
│   ├── config.py           # 配置管理
│   ├── database.py         # 数据库连接
│   └── main.py             # 应用入口
├── prometheus/             # Prometheus配置
├── storage/                # 数据存储目录
├── tests/                  # 测试集
├── alembic.ini             # Alembic配置
├── Dockerfile              # Docker构建文件
├── docker-compose.yml      # Docker Compose配置
├── requirements.txt        # Python依赖
└── start.sh                # 启动脚本
```

## API文档

启动服务后，可通过以下地址访问API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 监控与维护

H-Pulse·Mirage内置了完整的监控系统，能够跟踪以下指标：
- API请求计数和延迟统计
- 活跃用户数量
- 角色创建和模拟次数
- NFT铸造和交易统计
- 系统资源使用情况
- 异常发生率

通过Grafana可视化这些指标：http://localhost:3000

## 架构设计原则

本项目遵循以下设计原则：

1. **模块化设计**：各功能模块高内聚低耦合，方便扩展和维护
2. **RESTful API设计**：遵循REST规范设计接口
3. **领域驱动设计(DDD)**：基于业务领域构建系统结构
4. **可观测性设计**：内置监控、日志和追踪系统
5. **安全优先**：实现了JWT认证、参数验证等安全机制

## 贡献指南

欢迎贡献代码和提交问题！具体方法：

1. Fork本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个Pull Request

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件

## 云端部署指南

H-Pulse·Mirage 可以部署在各种云平台上，以下是推荐的部署方法：

### 1. 准备工作

1. 设置环境变量
   - 创建包含生产环境配置的`.env.production`文件
   - 确保设置了安全的`SECRET_KEY`和数据库凭证

2. 数据持久化
   - 确保所有持久化卷配置正确
   - 配置定期备份

### 2. 部署选项

#### AWS ECS/EKS

1. 构建并推送Docker镜像到ECR
   ```bash
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws-account>.dkr.ecr.<region>.amazonaws.com
   docker build -t h-pulse-mirage .
   docker tag h-pulse-mirage:latest <aws-account>.dkr.ecr.<region>.amazonaws.com/h-pulse-mirage:latest
   docker push <aws-account>.dkr.ecr.<region>.amazonaws.com/h-pulse-mirage:latest
   ```

2. 使用ECS任务定义或Kubernetes配置部署

#### 阿里云容器服务

1. 创建容器服务实例
2. 使用`docker-compose.yml`配置部署

### 3. 数据库配置

- 推荐使用托管数据库服务（RDS, ApsaraDB）
- 设置数据库连接字符串环境变量

### 4. 负载均衡和扩展

- 配置负载均衡器（ALB, NLB, SLB）
- 设置自动扩展规则

### 5. 监控与日志

- 配置监控告警
- 集成日志管理（CloudWatch, SLS）

## 环境变量

| 变量名 | 说明 | 默认值 | 是否必需 |
|--------|------|--------|----------|
| `DATABASE_URL` | 数据库连接URL | `postgresql://postgres:postgres@db:5432/h_pulse_mirage` | 是 |
| `SECRET_KEY` | JWT密钥 | `h_pulse_mirage_secret_key_change_in_production` | 是 |
| `DEBUG` | 调试模式 | `False` | 否 |
| `STORAGE_PATH` | 文件存储路径 | `./storage` | 否 |
| `POSTGRES_PASSWORD` | PostgreSQL密码 | `postgres` | 否 |
| `GRAFANA_USER` | Grafana管理员用户名 | `admin` | 否 |
| `GRAFANA_PASSWORD` | Grafana管理员密码 | `admin` | 否 |
| `HOST` | 主机地址 | `0.0.0.0` | 否 |
| `PORT` | 端口号 | `8000` | 否 |
| `WORKERS` | 工作进程数 | `1` | 否 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 | 