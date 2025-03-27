from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.destiny import DestinyNode
from app.schemas.destiny_schema import (
    DestinyInput, DestinyOutput, DestinyUpdate, 
    DestinyTree, DestinyPrediction
)
from app.models.character import Character
from app.core.fate_engine import update_fate_score
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/record", response_model=DestinyOutput, status_code=status.HTTP_201_CREATED)
def record_destiny_event(
    data: DestinyInput, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    记录命运事件
    
    记录一个新的命运事件，更新角色的命运评分
    
    Args:
        data: 命运事件数据
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        新创建的命运事件
        
    Raises:
        HTTPException: 如果角色不存在或无权操作
    """
    # 验证角色存在且归当前用户所有
    character = db.query(Character).filter(Character.id == data.character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权为此角色记录命运事件")
    
    # 验证父节点存在（如果提供了parent_id）
    if data.parent_id:
        parent_node = db.query(DestinyNode).filter(DestinyNode.id == data.parent_id).first()
        if not parent_node:
            raise HTTPException(status_code=404, detail="父节点事件不存在")
        if parent_node.character_id != data.character_id:
            raise HTTPException(status_code=400, detail="父节点必须属于同一角色")
    
    try:
        # 创建命运节点
        destiny = DestinyNode(
            character_id=data.character_id,
            event_name=data.event_name,
            event_type=data.event_type,
            decision=data.decision,
            result=data.result,
            consequence=data.consequence,
            description=data.description,
            tags=data.tags,
            parent_id=data.parent_id,
            impact_level=5.0  # 默认中等影响
        )
        db.add(destiny)
        
        # 更新命运评分
        character.fate_score = update_fate_score(character, data)
        
        db.commit()
        db.refresh(destiny)
        return destiny
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="记录命运事件失败，请稍后再试")

@router.get("/character/{character_id}/history", response_model=List[DestinyOutput])
def get_destiny_history(
    character_id: int = Path(..., gt=0),
    skip: int = 0,
    limit: int = 20,
    event_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    is_critical: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取角色的命运事件历史
    
    Args:
        character_id: 角色ID
        skip: 分页偏移量
        limit: 分页大小
        event_type: 事件类型过滤
        start_date: 开始日期过滤（格式：YYYY-MM-DD）
        end_date: 结束日期过滤（格式：YYYY-MM-DD）
        is_critical: 是否关键事件
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        命运事件列表
        
    Raises:
        HTTPException: 如果角色不存在或无权访问
    """
    # 验证角色存在且归当前用户所有
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此角色的命运事件")
    
    # 构建查询
    query = db.query(DestinyNode).filter(DestinyNode.character_id == character_id)
    
    if event_type:
        query = query.filter(DestinyNode.event_type == event_type)
    
    if start_date:
        from datetime import datetime
        try:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(DestinyNode.timestamp >= start_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="开始日期格式无效，应为YYYY-MM-DD")
    
    if end_date:
        from datetime import datetime
        try:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
            # 设置为当天结束
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
            query = query.filter(DestinyNode.timestamp <= end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="结束日期格式无效，应为YYYY-MM-DD")
    
    if is_critical is not None:
        query = query.filter(DestinyNode.is_critical == is_critical)
    
    # 排序并分页
    events = query.order_by(DestinyNode.timestamp.desc()).offset(skip).limit(limit).all()
    return events

@router.get("/{event_id}", response_model=DestinyOutput)
def get_destiny_event(
    event_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取命运事件详情
    
    Args:
        event_id: 事件ID
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        命运事件详情
        
    Raises:
        HTTPException: 如果事件不存在或无权访问
    """
    event = db.query(DestinyNode).filter(DestinyNode.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="命运事件不存在")
    
    # 验证事件关联的角色归当前用户所有
    character = db.query(Character).filter(Character.id == event.character_id).first()
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此命运事件")
    
    return event

@router.put("/{event_id}", response_model=DestinyOutput)
def update_destiny_event(
    event_id: int,
    event_update: DestinyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新命运事件
    
    Args:
        event_id: 事件ID
        event_update: 待更新的事件数据
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        更新后的命运事件
        
    Raises:
        HTTPException: 如果事件不存在或无权访问
    """
    event = db.query(DestinyNode).filter(DestinyNode.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="命运事件不存在")
    
    # 验证事件关联的角色归当前用户所有
    character = db.query(Character).filter(Character.id == event.character_id).first()
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权更新此命运事件")
    
    # 更新字段
    if event_update.event_name:
        event.event_name = event_update.event_name
    if event_update.decision:
        event.decision = event_update.decision
    if event_update.result:
        event.result = event_update.result
    if event_update.consequence:
        # 合并字典，保留原始字段
        existing_consequence = event.consequence if event.consequence else {}
        existing_consequence.update(event_update.consequence)
        event.consequence = existing_consequence
    if event_update.description is not None:
        event.description = event_update.description
    if event_update.tags is not None:
        event.tags = event_update.tags
    if event_update.is_critical is not None:
        event.is_critical = event_update.is_critical
    if event_update.impact_level is not None:
        event.impact_level = event_update.impact_level
    
    try:
        db.commit()
        db.refresh(event)
        return event
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="更新命运事件失败，请稍后再试")

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_destiny_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除命运事件
    
    Args:
        event_id: 事件ID
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Raises:
        HTTPException: 如果事件不存在或无权访问
    """
    event = db.query(DestinyNode).filter(DestinyNode.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="命运事件不存在")
    
    # 验证事件关联的角色归当前用户所有
    character = db.query(Character).filter(Character.id == event.character_id).first()
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此命运事件")
    
    db.delete(event)
    db.commit()
    return {"detail": "命运事件已删除"}

@router.get("/character/{character_id}/tree", response_model=DestinyTree)
def get_destiny_tree(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取角色的命运树
    
    Args:
        character_id: 角色ID
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        命运树结构，包含所有节点
        
    Raises:
        HTTPException: 如果角色不存在或无权访问
    """
    # 验证角色存在且归当前用户所有
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此角色的命运树")
    
    # 查询所有事件
    events = db.query(DestinyNode).filter(DestinyNode.character_id == character_id).all()
    
    # 查找根节点（没有父节点的节点）
    root_event = db.query(DestinyNode).filter(
        DestinyNode.character_id == character_id,
        DestinyNode.parent_id == None
    ).order_by(DestinyNode.timestamp.asc()).first()
    
    root_id = root_event.id if root_event else None
    
    return {
        "nodes": events,
        "root_id": root_id
    }

@router.get("/{event_id}/predict", response_model=DestinyPrediction)
def predict_destiny_paths(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    预测基于特定事件的命运路径
    
    Args:
        event_id: 基准事件ID
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        命运预测，包含可能的命运路径
        
    Raises:
        HTTPException: 如果事件不存在或无权访问
    """
    # 验证事件存在
    event = db.query(DestinyNode).filter(DestinyNode.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="命运事件不存在")
    
    # 验证事件关联的角色归当前用户所有
    character = db.query(Character).filter(Character.id == event.character_id).first()
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此事件预测")
    
    # 基于事件类型和角色特性生成预测路径
    # 此处为示例逻辑，实际应用中可能需要更复杂的预测算法
    import random
    
    # 根据事件类型和角色特性生成预测路径
    possible_paths = []
    
    # 不同事件类型对应不同的可能路径
    if event.event_type == "情感":
        possible_paths = [
            {
                "event_name": "继续投入情感",
                "probability": 0.6 + character.personality.get("E", 0) * 0.2,
                "consequence": {"happiness": 0.3, "vulnerability": 0.2}
            },
            {
                "event_name": "保持距离",
                "probability": 0.4 - character.personality.get("E", 0) * 0.2,
                "consequence": {"loneliness": 0.2, "independence": 0.3}
            }
        ]
    elif event.event_type == "决策":
        possible_paths = [
            {
                "event_name": "坚持原则",
                "probability": 0.5 + character.personality.get("C", 0) * 0.3,
                "consequence": {"reputation": 0.2, "stress": 0.1}
            },
            {
                "event_name": "妥协让步",
                "probability": 0.3 + character.personality.get("A", 0) * 0.2,
                "consequence": {"immediate_gain": 0.2, "self_doubt": 0.1}
            },
            {
                "event_name": "另辟蹊径",
                "probability": 0.2 + character.personality.get("O", 0) * 0.3,
                "consequence": {"innovation": 0.3, "uncertainty": 0.3}
            }
        ]
    else:
        # 默认生成两条随机路径
        possible_paths = [
            {
                "event_name": f"路径A: {event.event_name}的后续发展",
                "probability": 0.7,
                "consequence": {"factor1": random.uniform(0, 0.3), "factor2": random.uniform(-0.2, 0.2)}
            },
            {
                "event_name": f"路径B: {event.event_name}的另一种后果",
                "probability": 0.3,
                "consequence": {"factor1": random.uniform(-0.3, 0), "factor2": random.uniform(0, 0.3)}
            }
        ]
    
    # 计算概率系数
    probability_factors = {
        "personality": 0.4,  # 人格影响
        "past_decisions": 0.3,  # 过往决策影响
        "external_factors": 0.3  # 外部因素影响
    }
    
    return {
        "based_on_event_id": event_id,
        "possible_paths": possible_paths,
        "probability_factors": probability_factors
    } 