from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import logging
from app.config import settings

# 配置日志
logger = logging.getLogger(__name__)

# 数据库引擎配置
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,  # 30秒连接超时
    pool_recycle=1800,  # 30分钟回收连接
    echo=settings.DEBUG,  # 在DEBUG模式下打印SQL语句
)

# 数据库连接事件监听
@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    logger.info("Database connection established")

@event.listens_for(engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    logger.debug("Database connection checked out")

@event.listens_for(engine, "disconnect")
def disconnect(dbapi_connection, connection_record):
    logger.info("Database connection closed")

# Session工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础模型类
class CustomBase:
    @declared_attr
    def __tablename__(cls):
        # 自动生成小写表名
        return cls.__name__.lower()

Base = declarative_base(cls=CustomBase)

# FastAPI依赖项函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 上下文管理器，用于非依赖项的数据库会话需求
@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        session.close()

# 测试数据库连接
def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

# 初始化数据库表
def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created") 