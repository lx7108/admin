from sqlalchemy import create_engine
from app.database import Base
from app.config import settings

def init_db():
    engine = create_engine(settings.DATABASE_URL, echo=True, future=True)
    Base.metadata.create_all(engine)
    print("数据库初始化完成")

if __name__ == "__main__":
    init_db()
