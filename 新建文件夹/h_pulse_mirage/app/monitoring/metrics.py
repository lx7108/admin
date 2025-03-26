from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
import time
import threading
import psutil
import os
import logging

logger = logging.getLogger(__name__)

# 请求计数器
REQUEST_COUNT = Counter(
    "h_pulse_http_requests_total", 
    "Total HTTP Requests",
    ["method", "endpoint", "http_status"]
)

# 请求延迟直方图
REQUEST_LATENCY = Histogram(
    "h_pulse_http_request_latency_seconds", 
    "HTTP Request latency",
    ["endpoint"]
)

# 活跃用户计数
ACTIVE_USERS = Gauge(
    "h_pulse_active_users", 
    "Number of users currently logged in"
)

# 角色创建计数器
CHARACTER_CREATION = Counter(
    "h_pulse_character_creation_total", 
    "Total characters created"
)

# 角色模拟计数器
CHARACTER_SIMULATION = Counter(
    "h_pulse_character_simulation_total", 
    "Total character simulations run"
)

# NFT铸造计数器
NFT_MINTED = Counter(
    "h_pulse_nft_minted_total", 
    "Total NFTs minted"
)

# NFT交易计数器
NFT_TRADED = Counter(
    "h_pulse_nft_traded_total", 
    "Total NFTs traded"
)

# 系统资源指标
SYSTEM_CPU_USAGE = Gauge(
    "h_pulse_system_cpu_usage", 
    "System CPU usage percentage"
)

SYSTEM_MEMORY_USAGE = Gauge(
    "h_pulse_system_memory_usage", 
    "System memory usage percentage"
)

SYSTEM_DISK_USAGE = Gauge(
    "h_pulse_system_disk_usage", 
    "System disk usage percentage"
)

# 命运事件统计
DESTINY_EVENTS = Counter(
    "h_pulse_destiny_events_total", 
    "Total destiny events recorded",
    ["event_type"]
)

# 异常计数器
EXCEPTIONS = Counter(
    "h_pulse_exceptions_total", 
    "Total exceptions raised",
    ["type"]
)

# 缓存命中率
CACHE_HIT_RATE = Summary(
    "h_pulse_cache_hit_rate", 
    "Cache hit rate percentage"
)

# 数据库操作计数和延迟
DB_OPERATIONS = Counter(
    "h_pulse_db_operations_total",
    "Total database operations",
    ["operation_type"]
)

DB_OPERATION_LATENCY = Histogram(
    "h_pulse_db_operation_latency_seconds",
    "Database operation latency",
    ["operation_type"]
)

# API健康状态
API_HEALTH = Gauge(
    "h_pulse_api_health",
    "API health status (1 = healthy, 0 = unhealthy)"
)

# 应用启动时间
APP_UPTIME = Gauge(
    "h_pulse_app_uptime_seconds",
    "Application uptime in seconds"
)

# WebSocket连接计数
WS_CONNECTIONS = Gauge(
    "h_pulse_ws_connections",
    "Current WebSocket connections"
)

def setup_metrics(app):
    """设置监控中间件"""
    # 记录应用启动时间
    start_time = time.time()
    
    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        endpoint = request.url.path
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(process_time)
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=response.status_code).inc()

        return response

    @app.get("/metrics")
    async def metrics():
        """导出Prometheus指标"""
        # 更新系统指标
        update_system_metrics()
        
        # 更新应用运行时间
        APP_UPTIME.set(time.time() - start_time)
        
        try:
            return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
        except Exception as e:
            logger.error(f"生成监控指标时出错: {str(e)}")
            record_exception("metrics_generation")
            return Response(
                content="Error generating metrics",
                status_code=500
            )
    
    # 启动后台线程定期更新系统指标
    metrics_thread = threading.Thread(target=start_metrics_collection, daemon=True)
    metrics_thread.start()

def update_system_metrics():
    """更新系统资源指标"""
    try:
        # CPU使用率
        SYSTEM_CPU_USAGE.set(psutil.cpu_percent())
        
        # 内存使用率
        memory = psutil.virtual_memory()
        SYSTEM_MEMORY_USAGE.set(memory.percent)
        
        # 磁盘使用率
        disk = psutil.disk_usage(os.path.abspath(os.sep))
        SYSTEM_DISK_USAGE.set(disk.percent)
    except Exception as e:
        logger.error(f"更新系统指标时出错: {str(e)}")

def start_metrics_collection():
    """开始后台指标收集"""
    import time
    while True:
        try:
            update_system_metrics()
            time.sleep(15)  # 每15秒更新一次
        except Exception as e:
            logger.error(f"指标收集线程出错: {str(e)}")
            time.sleep(30)  # 出错后等待更长时间

# 业务指标更新函数
def increment_active_users(value=1):
    """增加/减少活跃用户计数"""
    ACTIVE_USERS.inc(value)

def decrement_active_users(value=1):
    """减少活跃用户计数"""
    ACTIVE_USERS.dec(value)

def record_character_creation():
    """记录角色创建"""
    CHARACTER_CREATION.inc()

def record_character_simulation():
    """记录角色模拟"""
    CHARACTER_SIMULATION.inc()

def record_nft_minted():
    """记录NFT铸造"""
    NFT_MINTED.inc()

def record_nft_traded():
    """记录NFT交易"""
    NFT_TRADED.inc()

def record_destiny_event(event_type):
    """记录命运事件"""
    DESTINY_EVENTS.labels(event_type=event_type).inc()

def record_exception(exception_type):
    """记录异常"""
    EXCEPTIONS.labels(type=exception_type).inc()

def record_cache_hit_rate(hit_rate):
    """记录缓存命中率"""
    CACHE_HIT_RATE.observe(hit_rate)
    
def record_db_operation(operation_type, duration=None):
    """记录数据库操作"""
    DB_OPERATIONS.labels(operation_type=operation_type).inc()
    if duration:
        DB_OPERATION_LATENCY.labels(operation_type=operation_type).observe(duration)

def set_api_health(is_healthy):
    """设置API健康状态"""
    API_HEALTH.set(1 if is_healthy else 0)

def increment_ws_connections():
    """增加WebSocket连接计数"""
    WS_CONNECTIONS.inc()
    
def decrement_ws_connections():
    """减少WebSocket连接计数"""
    WS_CONNECTIONS.dec() 