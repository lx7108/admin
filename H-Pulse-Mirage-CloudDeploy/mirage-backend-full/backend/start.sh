#!/bin/bash

# 确保脚本在错误时停止执行
set -e

# 输出环境信息
echo "=== H-Pulse·Mirage 启动 ==="
echo "环境: $([ "$DEBUG" == "True" ] && echo "开发" || echo "生产")"
echo "数据库URL: $DATABASE_URL"
echo "存储路径: $STORAGE_PATH"

# 检查必要的环境变量
if [ -z "$SECRET_KEY" ]; then
    echo "警告: SECRET_KEY 未设置，使用默认值"
fi

# 确保存储目录存在且有正确权限
mkdir -p $STORAGE_PATH
chmod -R 777 $STORAGE_PATH
echo "存储目录已准备就绪: $STORAGE_PATH"

# 等待数据库准备就绪
echo "等待数据库准备就绪..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "数据库已就绪!"

# 运行数据库迁移
echo "运行数据库迁移..."
alembic upgrade head

# 检查是否需要创建初始数据
python -c "
from app.database import engine, Base, get_db_session
from app.models.society import Regime
with get_db_session() as session:
    if not session.query(Regime).first():
        print('正在创建初始数据...')
        from app.models.society import SocialClass
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # 创建默认管理员
        if not session.query(User).filter(User.username == 'admin').first():
            admin = User(username='admin', email='admin@example.com', hashed_password=get_password_hash('admin'), is_active=True, is_verified=True)
            session.add(admin)
            session.commit()
            
        # 创建默认政权
        regime = Regime(name='默认政权', type='民主', satisfaction=0.6, corruption=0.3, stability=0.7, prosperity=0.5, freedom=0.7)
        session.add(regime)
        session.commit()
        
        # 创建默认社会阶层
        classes = [
            SocialClass(regime_id=regime.id, name='统治阶层', wealth=0.8, population_ratio=0.1, influence=0.7, education=0.8, health=0.8, happiness=0.7, mobility=0.3),
            SocialClass(regime_id=regime.id, name='中产阶级', wealth=0.5, population_ratio=0.3, influence=0.4, education=0.6, health=0.6, happiness=0.6, mobility=0.5),
            SocialClass(regime_id=regime.id, name='底层民众', wealth=0.2, population_ratio=0.6, influence=0.2, education=0.4, health=0.4, happiness=0.4, mobility=0.2)
        ]
        for class_obj in classes:
            session.add(class_obj)
        session.commit()
        
        print('初始数据创建完成!')
    else:
        print('初始数据已存在，跳过创建')
"

# 启动应用
echo "启动 H-Pulse·Mirage 命运模拟与演出引擎..."
if [ "$DEBUG" == "True" ]; then
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi 