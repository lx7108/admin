from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings

def test_connection():
    try:
        engine = create_engine(settings.DATABASE_URL, future=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("数据库连接成功")
        return True
    except SQLAlchemyError as e:
        print(f"数据库连接失败: {e}")
        return False

if __name__ == "__main__":
    test_connection()
