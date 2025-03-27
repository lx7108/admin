from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.engine.drama_builder import generate_fate_theater
from app.models.causal_node import CausalEvent

router = APIRouter()

@router.get("/script/{event_id}")
def get_fate_script(event_id: int, db: Session = Depends(get_db)):
    """
    获取特定事件的命运剧场脚本
    
    Args:
        event_id: 事件ID（作为溯源起点）
        
    Returns:
        命运剧场脚本对象
    """
    # 检查事件是否存在
    event = db.query(CausalEvent).filter(CausalEvent.id == event_id).first()
    if not event:
        return {"error": "事件不存在"}
    
    # 生成命运剧场脚本
    script = generate_fate_theater(event_id, db)
    return script

@router.get("/character/{character_id}/events")
def get_character_events(character_id: int, db: Session = Depends(get_db)):
    """获取特定角色的所有事件"""
    events = db.query(CausalEvent).filter(CausalEvent.actor_id == character_id).all()
    
    if not events:
        return {"events": []}
    
    event_list = []
    for e in events:
        event_list.append({
            "id": e.id,
            "action": e.action,
            "timestamp": e.timestamp.strftime("%Y-%m-%d %H:%M")
        })
    
    return {"events": event_list} 