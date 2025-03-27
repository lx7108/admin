from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.character import Character
from app.models.society import Regime, SocialClass
from datetime import datetime

def seed_data():
    db: Session = SessionLocal()

    user = User(username="admin", email="admin@example.com", hashed_password="fakehashedpassword")
    db.add(user)
    db.commit()
    db.refresh(user)

    char = Character(user_id=user.id, name="模拟角色", birth_time="1997-07-16 11:50",
                     attributes={"体魄": 0.6, "智力": 0.7}, personality={"O": 0.6, "C": 0.5})
    db.add(char)

    regime = Regime(name="乌托邦", type="AI极权", satisfaction=0.8)
    db.add(regime)
    db.commit()
    db.refresh(regime)

    for name, ratio in [("统治阶层", 0.1), ("中产阶层", 0.4), ("底层民众", 0.5)]:
        cls = SocialClass(regime_id=regime.id, name=name, population_ratio=ratio)
        db.add(cls)

    db.commit()
    db.close()
    print("初始数据已插入")

if __name__ == "__main__":
    seed_data()
