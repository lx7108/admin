from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.character import Character
from app.pvp_arena.arena_engine import simulate_duel

router = APIRouter()

@router.post("/simulate")
def run_character_duel(character_id_1: int, character_id_2: int, db: Session = Depends(get_db)):
    """
    模拟两个角色的对抗互动
    
    Args:
        character_id_1: 第一个角色ID
        character_id_2: 第二个角色ID
        
    Returns:
        对抗互动记录，包含对抗流程和对白
    """
    # 获取角色数据
    char1 = db.query(Character).filter(Character.id == character_id_1).first()
    char2 = db.query(Character).filter(Character.id == character_id_2).first()
    
    if not char1 or not char2:
        return {"error": "角色不存在"}
    
    # 将角色数据转换为AI可用的配置文件
    profile1 = char1.to_profile()
    profile2 = char2.to_profile()
    
    # 执行对抗模拟
    duel_result = simulate_duel(profile1, profile2, rounds=10)
    
    return duel_result

@router.get("/history/{character_id}")
def get_duel_history(character_id: int, db: Session = Depends(get_db)):
    """获取角色的对抗历史"""
    # 这里可以实现从数据库中查询对抗历史的逻辑
    # 暂时返回模拟数据
    return {
        "character_id": character_id,
        "duels": [
            {"opponent_id": 2, "result": "胜利", "date": "2025-03-25"},
            {"opponent_id": 4, "result": "失败", "date": "2025-03-26"}
        ]
    } 