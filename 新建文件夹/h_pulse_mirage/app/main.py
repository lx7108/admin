from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import time
import socket
import platform

from app.routers import user_router, character_router, society_router, destiny_router, theater_router, nft_router, pvp_router, simulation_router
from app.database import Base, engine, test_connection, init_db
from app.monitoring.metrics import setup_metrics
from app.middleware.logger import ErrorLoggerMiddleware
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME, 
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 接入监控
setup_metrics(app)

# 接入异常日志中间件
app.add_middleware(ErrorLoggerMiddleware)

# 路由注册
API_PREFIX = settings.API_PREFIX
app.include_router(user_router.router, prefix=f"{API_PREFIX}/user", tags=["User"])
app.include_router(character_router.router, prefix=f"{API_PREFIX}/character", tags=["Character"])
app.include_router(society_router.router, prefix=f"{API_PREFIX}/society", tags=["Society"])
app.include_router(destiny_router.router, prefix=f"{API_PREFIX}/destiny", tags=["Destiny"])
app.include_router(theater_router.router, prefix=f"{API_PREFIX}/theater", tags=["Theater"])
app.include_router(nft_router.router, prefix=f"{API_PREFIX}/nft", tags=["NFT"])
app.include_router(pvp_router.router, prefix=f"{API_PREFIX}/pvp", tags=["PvP"])
app.include_router(simulation_router.router, prefix=f"{API_PREFIX}/simulation", tags=["Simulation"])

# 创建存储目录
os.makedirs(settings.STORAGE_PATH, exist_ok=True)

# 如果目录存在，挂载静态文件
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 请求处理时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# 健康检查端点
@app.get(f"{API_PREFIX}/health")
async def health_check():
    db_connected = test_connection()
    storage_writable = os.access(settings.STORAGE_PATH, os.W_OK)
    
    status = "healthy" if db_connected and storage_writable else "unhealthy"
    status_code = 200 if status == "healthy" else 503
    
    result = {
        "status": status,
        "version": settings.APP_VERSION,
        "db_connected": db_connected,
        "storage_writable": storage_writable,
        "environment": "production" if not settings.DEBUG else "development"
    }
    
    return JSONResponse(content=result, status_code=status_code)

# 监控节点端点
@app.get(f"{API_PREFIX}/monitoring/node")
async def node_info():
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "uptime": time.time()
    }

# 初始化数据库（仅在调试模式下）
if settings.DEBUG:
    init_db()

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "description": settings.APP_DESCRIPTION,
        "docs_url": "/docs",
        "version": settings.APP_VERSION
    } 