from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.character import Character
from app.models.destiny import DestinyNode
from app.schemas.character_schema import (
    CharacterCreate, CharacterOut, CharacterUpdate, 
    CharacterBrief, CharacterWithEvents, CharacterWithRelationships
)
from app.core.bazi_engine import analyze_character_fate
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/create", response_model=CharacterOut, status_code=status.HTTP_201_CREATED)
def create_character(
    character: CharacterCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新角色
    
    根据提供的信息创建一个新角色，包括命理分析和初始属性生成
    
    Args:
        character: 角色创建数据
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        新创建的角色信息
        
    Raises:
        HTTPException: 如果创建角色失败
    """
    # 验证用户ID是否合法
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能为自己创建角色")
    
    # 分析角色命理
    fate_analysis = analyze_character_fate(character.birth_time)
    
    # 根据命理分析生成初始属性
    # 使用五行分布影响属性值的生成
    wuxing = fate_analysis["五行分析"]["分布"]
    import random
    
    # 根据五行分布调整属性生成的权重
    physique_weight = 1.0 + (wuxing.get("土", 0) + wuxing.get("金", 0)) * 0.05
    intelligence_weight = 1.0 + (wuxing.get("水", 0) + wuxing.get("木", 0)) * 0.05
    emotion_weight = 1.0 + (wuxing.get("火", 0) + wuxing.get("水", 0)) * 0.05
    social_weight = 1.0 + (wuxing.get("木", 0) + wuxing.get("火", 0)) * 0.05
    
    attr = {
        "physique": min(10, max(1, round(random.randint(1, 10) * physique_weight))),
        "intelligence": min(10, max(1, round(random.randint(1, 10) * intelligence_weight))),
        "emotion": min(10, max(1, round(random.randint(1, 10) * emotion_weight))),
        "social": min(10, max(1, round(random.randint(1, 10) * social_weight))),
        "wuxing": wuxing
    }
    
    # 生成基于五行的人格特质
    # 每个五行对应一个特质的偏向
    dominant = fate_analysis["五行分析"]["主导五行"]
    personality_base = {
        "O": 0.5, "C": 0.5, "E": 0.5, "A": 0.5, "N": 0.5
    }
    
    # 根据主导五行调整人格
    if dominant == "木":
        personality_base["O"] += 0.2  # 木主创新
        personality_base["C"] -= 0.1
    elif dominant == "火":
        personality_base["E"] += 0.2  # 火主外向
        personality_base["N"] += 0.1
    elif dominant == "土":
        personality_base["A"] += 0.2  # 土主和善
        personality_base["O"] -= 0.1
    elif dominant == "金":
        personality_base["C"] += 0.2  # 金主条理
        personality_base["E"] -= 0.1
    elif dominant == "水":
        personality_base["O"] += 0.1  # 水主智慧
        personality_base["N"] -= 0.1
    
    # 加入随机波动，确保人格多样性
    personality = {
        trait: min(1.0, max(0.0, value + (random.random() - 0.5) * 0.4))
        for trait, value in personality_base.items()
    }
    
    try:
        # 创建角色
        char = Character(
            user_id=character.user_id,
            name=character.name,
            birth_time=character.birth_time,
            attributes=attr,
            personality=personality,
            destiny_tree={"start": "born"},
            fate_score=fate_analysis["命运评分"],
            background_story=character.background_story,
            avatar_url=character.avatar_url,
            bazi_summary={
                "八字": fate_analysis["八字排盘"],
                "五行": fate_analysis["五行分析"]
            }
        )
        db.add(char)
        db.commit()
        db.refresh(char)
        return char
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="创建角色失败，请稍后再试")

@router.get("", response_model=List[CharacterBrief])
def get_characters(
    skip: int = 0, 
    limit: int = 10,
    name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取角色列表
    
    Args:
        skip: 分页偏移量
        limit: 分页大小
        name: 按名称过滤（可选）
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        角色列表
    """
    query = db.query(Character).filter(Character.user_id == current_user.id)
    
    if name:
        query = query.filter(Character.name.ilike(f"%{name}%"))
    
    return query.offset(skip).limit(limit).all()

@router.get("/{character_id}", response_model=CharacterOut)
def get_character(
    character_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取角色详情
    
    Args:
        character_id: 角色ID
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        角色详情
        
    Raises:
        HTTPException: 如果角色不存在或无权访问
    """
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 验证权限（只能访问自己的角色）
    if char.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此角色")
        
    return char

@router.put("/{character_id}", response_model=CharacterOut)
def update_character(
    character_id: int,
    character_update: CharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新角色信息
    
    Args:
        character_id: 角色ID
        character_update: 待更新的角色信息
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        更新后的角色信息
        
    Raises:
        HTTPException: 如果角色不存在或无权访问
    """
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 验证权限（只能更新自己的角色）
    if char.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权更新此角色")
    
    # 更新字段
    if character_update.name:
        char.name = character_update.name
    if character_update.background_story:
        char.background_story = character_update.background_story
    if character_update.avatar_url:
        char.avatar_url = character_update.avatar_url
    if character_update.attributes:
        # 合并字典而不是替换，保留原来的wuxing等关键信息
        char.attributes.update(character_update.attributes)
    if character_update.personality:
        char.personality.update(character_update.personality)
    
    try:
        db.commit()
        db.refresh(char)
        return char
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="更新角色失败，请稍后再试")

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除角色
    
    Args:
        character_id: 角色ID
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Raises:
        HTTPException: 如果角色不存在或无权访问
    """
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 验证权限（只能删除自己的角色）
    if char.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此角色")
        
    db.delete(char)
    db.commit()
    return {"detail": "角色已删除"}

@router.get("/{character_id}/events", response_model=CharacterWithEvents)
def get_character_events(
    character_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取角色的命运事件
    
    Args:
        character_id: 角色ID
        skip: 分页偏移量
        limit: 分页大小
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        角色信息和关联的命运事件
        
    Raises:
        HTTPException: 如果角色不存在或无权访问
    """
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 验证权限（只能查看自己的角色）
    if char.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此角色")
    
    # 获取角色关联的命运事件
    events = db.query(DestinyNode).filter(
        DestinyNode.character_id == character_id
    ).order_by(DestinyNode.timestamp.desc()).offset(skip).limit(limit).all()
    
    return {
        **char.__dict__,
        "destiny_nodes": events
    }

@router.get("/{character_id}/relationships", response_model=CharacterWithRelationships)
def get_character_relationships(
    character_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取角色的社会关系
    
    Args:
        character_id: 角色ID
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        角色信息和关联的社会关系
        
    Raises:
        HTTPException: 如果角色不存在或无权访问
    """
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 验证权限（只能查看自己的角色）
    if char.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此角色")
    
    # 获取所有与该角色相关的关系
    source_relations = char.relationships_source
    target_relations = char.relationships_target
    
    all_relationships = list(source_relations) + list(target_relations)
    
    return {
        **char.__dict__,
        "relationships": all_relationships
    } 