from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import random

from app.database import get_db
from app.models.society import Regime, SocialClass, SocialEvent, SocialClassEvent
from app.models.character import Character
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/regime", response_model=Dict[str, Any])
def get_regime_state(db: Session = Depends(get_db)):
    """
    获取当前政权状态
    
    Args:
        db: 数据库会话
        
    Returns:
        当前政权状态
    """
    regime = db.query(Regime).order_by(Regime.timestamp.desc()).first()
    if not regime:
        # 如果没有政权数据，创建默认政权
        regime = create_default_regime(db)
    
    return {
        "id": regime.id,
        "name": regime.name,
        "type": regime.type,
        "satisfaction": regime.satisfaction,
        "corruption": regime.corruption,
        "stability": regime.stability,
        "prosperity": regime.prosperity,
        "freedom": regime.freedom,
        "timestamp": regime.timestamp
    }

@router.get("/social-classes", response_model=List[Dict[str, Any]])
def get_social_classes(
    regime_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取社会阶层列表
    
    Args:
        regime_id: 政权ID过滤
        db: 数据库会话
        
    Returns:
        社会阶层列表
    """
    query = db.query(SocialClass)
    
    if regime_id:
        query = query.filter(SocialClass.regime_id == regime_id)
    
    classes = query.all()
    
    if not classes and regime_id:
        # 如果没有对应政权的阶层数据，创建默认阶层
        regime = db.query(Regime).filter(Regime.id == regime_id).first()
        if regime:
            classes = create_default_social_classes(db, regime.id)
    
    return [
        {
            "id": c.id,
            "name": c.name,
            "wealth": c.wealth,
            "population_ratio": c.population_ratio,
            "influence": c.influence,
            "education": c.education,
            "health": c.health,
            "happiness": c.happiness,
            "mobility": c.mobility
        } for c in classes
    ]

@router.get("/status", response_model=Dict[str, Any])
def get_social_status(db: Session = Depends(get_db)):
    """
    获取社会状态摘要
    
    Args:
        db: 数据库会话
        
    Returns:
        社会状态摘要
    """
    regime = db.query(Regime).order_by(Regime.timestamp.desc()).first()
    if not regime:
        return {"turbulence": "平稳", "relationships": "正常"}
    
    # 简单计算社会动荡程度
    turbulence = "危险" if regime.corruption > 0.7 else "紧张" if regime.corruption > 0.4 else "平稳"
    relationship_status = "紧张" if regime.satisfaction < 0.3 else "正常"
    
    # 社会事件影响
    recent_events = db.query(SocialEvent).filter(
        SocialEvent.regime_id == regime.id,
        SocialEvent.is_active == True
    ).order_by(SocialEvent.timestamp.desc()).limit(3).all()
    
    events_summary = []
    for event in recent_events:
        events_summary.append({
            "name": event.name,
            "type": event.event_type,
            "started": event.timestamp.strftime("%Y-%m-%d")
        })
    
    return {
        "turbulence": turbulence,
        "relationships": relationship_status,
        "regime_type": regime.type,
        "prosperity": regime.prosperity,
        "events": events_summary
    }

@router.post("/regime", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def create_regime(
    name: str,
    regime_type: str, 
    satisfaction: float = 0.5,
    corruption: float = 0.2,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新政权
    
    Args:
        name: 政权名称
        regime_type: 政权类型
        satisfaction: 满意度
        corruption: 腐败程度
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        新创建的政权
    """
    # 检查用户权限（此处简化处理，实际应有更复杂的权限管理）
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="无权创建政权")
    
    # 创建新政权
    new_regime = Regime(
        name=name,
        type=regime_type,
        satisfaction=satisfaction,
        corruption=corruption,
        stability=0.5,
        prosperity=0.5,
        freedom=0.5 if regime_type == "民主" else 0.3
    )
    
    db.add(new_regime)
    db.commit()
    db.refresh(new_regime)
    
    # 创建对应的社会阶层
    create_default_social_classes(db, new_regime.id)
    
    return {
        "id": new_regime.id,
        "name": new_regime.name,
        "type": new_regime.type,
        "message": "政权创建成功"
    }

@router.post("/event", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def create_social_event(
    name: str,
    event_type: str,
    regime_id: int,
    description: Optional[str] = None,
    impact: Optional[Dict[str, float]] = None,
    duration: Optional[int] = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建社会事件
    
    Args:
        name: 事件名称
        event_type: 事件类型
        regime_id: 政权ID
        description: 事件描述
        impact: 事件影响
        duration: 持续时间（天）
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        新创建的社会事件
    """
    # 检查政权是否存在
    regime = db.query(Regime).filter(Regime.id == regime_id).first()
    if not regime:
        raise HTTPException(status_code=404, detail="政权不存在")
    
    # 检查用户权限
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="无权创建社会事件")
    
    # 默认影响
    if not impact:
        impact = generate_default_impact(event_type)
    
    # 创建社会事件
    new_event = SocialEvent(
        regime_id=regime_id,
        name=name,
        event_type=event_type,
        description=description,
        impact=impact,
        duration=duration,
        is_active=True
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    # 应用事件影响到政权
    apply_event_impact(regime, impact, db)
    
    # 对社会阶层产生影响
    apply_event_to_classes(new_event.id, regime_id, event_type, impact, db)
    
    return {
        "id": new_event.id,
        "name": new_event.name,
        "event_type": new_event.event_type,
        "message": "社会事件创建成功，已应用影响"
    }

@router.get("/events", response_model=List[Dict[str, Any]])
def get_social_events(
    regime_id: Optional[int] = None,
    active_only: bool = False,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取社会事件列表
    
    Args:
        regime_id: 政权ID过滤
        active_only: 是否只返回活跃事件
        skip: 分页偏移量
        limit: 分页大小
        db: 数据库会话
        
    Returns:
        社会事件列表
    """
    query = db.query(SocialEvent)
    
    if regime_id:
        query = query.filter(SocialEvent.regime_id == regime_id)
    
    if active_only:
        query = query.filter(SocialEvent.is_active == True)
    
    events = query.order_by(SocialEvent.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": event.id,
            "name": event.name,
            "event_type": event.event_type,
            "description": event.description,
            "impact": event.impact,
            "timestamp": event.timestamp,
            "duration": event.duration,
            "is_active": event.is_active,
            "regime_id": event.regime_id
        } for event in events
    ]

@router.get("/simulate/next", response_model=Dict[str, Any])
def simulate_next_social_change(
    steps: int = 1,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    模拟下一步社会变化
    
    Args:
        steps: 模拟步数
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        模拟结果
    """
    # 检查用户权限
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="无权执行社会模拟")
    
    # 获取当前政权
    regime = db.query(Regime).order_by(Regime.timestamp.desc()).first()
    if not regime:
        regime = create_default_regime(db)
    
    # 获取社会阶层
    classes = db.query(SocialClass).filter(SocialClass.regime_id == regime.id).all()
    if not classes:
        classes = create_default_social_classes(db, regime.id)
    
    # 模拟结果记录
    simulation_results = []
    
    # 执行模拟步骤
    for _ in range(steps):
        # 随机决定是否发生事件（30%概率）
        if random.random() < 0.3:
            # 创建随机事件
            event_type = random.choice(["革命", "改革", "战争", "灾难", "科技进步", "文化变革"])
            event_name = f"模拟{event_type}"
            impact = generate_default_impact(event_type)
            
            # 创建事件
            new_event = SocialEvent(
                regime_id=regime.id,
                name=event_name,
                event_type=event_type,
                description=f"模拟生成的{event_type}事件",
                impact=impact,
                duration=random.randint(10, 100),
                is_active=True
            )
            
            db.add(new_event)
            db.commit()
            db.refresh(new_event)
            
            # 应用事件影响
            apply_event_impact(regime, impact, db)
            apply_event_to_classes(new_event.id, regime.id, event_type, impact, db)
            
            simulation_results.append({
                "type": "event",
                "name": event_name,
                "event_type": event_type,
                "impact": impact
            })
        else:
            # 自然演化
            evolve_regime(regime, db)
            evolve_social_classes(classes, db)
            
            simulation_results.append({
                "type": "evolution",
                "regime_satisfaction": regime.satisfaction,
                "regime_corruption": regime.corruption,
                "classes_changes": [
                    {"name": c.name, "happiness": c.happiness} for c in classes
                ]
            })
    
    # 返回模拟结果和当前社会状态
    return {
        "steps_simulated": steps,
        "simulation_results": simulation_results,
        "current_state": {
            "regime": {
                "id": regime.id,
                "name": regime.name,
                "type": regime.type,
                "satisfaction": regime.satisfaction,
                "corruption": regime.corruption,
                "stability": regime.stability
            },
            "classes": [
                {"name": c.name, "happiness": c.happiness, "wealth": c.wealth} 
                for c in classes
            ]
        }
    }

# 辅助函数
def create_default_regime(db: Session) -> Regime:
    """创建默认政权"""
    regime = Regime(
        name="默认政权",
        type="民主",
        satisfaction=0.6,
        corruption=0.3,
        stability=0.7,
        prosperity=0.5,
        freedom=0.7
    )
    db.add(regime)
    db.commit()
    db.refresh(regime)
    return regime

def create_default_social_classes(db: Session, regime_id: int) -> List[SocialClass]:
    """创建默认社会阶层"""
    classes = [
        SocialClass(
            regime_id=regime_id,
            name="统治阶层",
            wealth=0.8,
            population_ratio=0.1,
            influence=0.7,
            education=0.8,
            health=0.8,
            happiness=0.7,
            mobility=0.3
        ),
        SocialClass(
            regime_id=regime_id,
            name="中产阶级",
            wealth=0.5,
            population_ratio=0.3,
            influence=0.4,
            education=0.6,
            health=0.6,
            happiness=0.6,
            mobility=0.5
        ),
        SocialClass(
            regime_id=regime_id,
            name="底层民众",
            wealth=0.2,
            population_ratio=0.6,
            influence=0.2,
            education=0.4,
            health=0.4,
            happiness=0.4,
            mobility=0.2
        )
    ]
    
    for class_obj in classes:
        db.add(class_obj)
    
    db.commit()
    
    # 刷新对象
    for class_obj in classes:
        db.refresh(class_obj)
    
    return classes

def generate_default_impact(event_type: str) -> Dict[str, float]:
    """根据事件类型生成默认影响"""
    if event_type == "革命":
        return {
            "satisfaction": -0.2,
            "corruption": -0.3,
            "stability": -0.4,
            "freedom": 0.3
        }
    elif event_type == "改革":
        return {
            "satisfaction": 0.2,
            "corruption": -0.1,
            "stability": 0.1,
            "prosperity": 0.2
        }
    elif event_type == "战争":
        return {
            "satisfaction": -0.3,
            "stability": -0.3,
            "prosperity": -0.4
        }
    elif event_type == "灾难":
        return {
            "satisfaction": -0.2,
            "stability": -0.2,
            "prosperity": -0.3,
            "health": -0.3
        }
    elif event_type == "科技进步":
        return {
            "prosperity": 0.3,
            "education": 0.2,
            "health": 0.1
        }
    elif event_type == "文化变革":
        return {
            "freedom": 0.2,
            "education": 0.2,
            "happiness": 0.1
        }
    else:
        # 默认影响
        return {
            "satisfaction": random.uniform(-0.1, 0.1),
            "corruption": random.uniform(-0.1, 0.1),
            "stability": random.uniform(-0.1, 0.1),
            "prosperity": random.uniform(-0.1, 0.1)
        }

def apply_event_impact(regime: Regime, impact: Dict[str, float], db: Session):
    """应用事件影响到政权"""
    for attr, delta in impact.items():
        if hasattr(regime, attr):
            current_val = getattr(regime, attr)
            new_val = max(0, min(1, current_val + delta))  # 确保在0-1范围内
            setattr(regime, attr, new_val)
    
    db.commit()

def apply_event_to_classes(
    event_id: int, 
    regime_id: int, 
    event_type: str, 
    impact: Dict[str, float], 
    db: Session
):
    """应用事件影响到社会阶层"""
    classes = db.query(SocialClass).filter(SocialClass.regime_id == regime_id).all()
    
    for class_obj in classes:
        # 不同事件对不同阶层的影响不同
        class_impact = 0.0
        
        if event_type == "革命":
            if class_obj.name == "统治阶层":
                class_impact = -0.3
            elif class_obj.name == "底层民众":
                class_impact = 0.2
        elif event_type == "改革":
            if class_obj.name == "中产阶级":
                class_impact = 0.2
        elif event_type == "战争":
            # 战争对所有阶层都有负面影响
            class_impact = -0.2
        elif event_type == "灾难":
            # 灾难对底层影响更大
            if class_obj.name == "底层民众":
                class_impact = -0.3
            else:
                class_impact = -0.1
        
        # 创建阶层事件影响记录
        class_event = SocialClassEvent(
            event_id=event_id,
            class_id=class_obj.id,
            impact=class_impact
        )
        db.add(class_event)
        
        # 应用影响到阶层状态
        class_obj.happiness = max(0, min(1, class_obj.happiness + class_impact * 0.5))
        
        # 事件类型特定影响
        if event_type == "科技进步":
            class_obj.education = max(0, min(1, class_obj.education + 0.1))
        elif event_type == "文化变革":
            class_obj.mobility = max(0, min(1, class_obj.mobility + 0.1))
    
    db.commit()

def evolve_regime(regime: Regime, db: Session):
    """模拟政权自然演化"""
    # 腐败与满意度负相关
    if regime.corruption > 0.5:
        regime.satisfaction = max(0, regime.satisfaction - 0.01)
    
    # 满意度与稳定性正相关
    regime.stability = (regime.stability * 0.9) + (regime.satisfaction * 0.1)
    
    # 自然腐败增长（如无反腐措施）
    regime.corruption = min(1, regime.corruption + 0.005)
    
    # 繁荣度自然变化
    regime.prosperity = max(0, min(1, regime.prosperity + random.uniform(-0.01, 0.01)))
    
    db.commit()

def evolve_social_classes(classes: List[SocialClass], db: Session):
    """模拟社会阶层自然演化"""
    for class_obj in classes:
        # 财富影响幸福感
        class_obj.happiness = (class_obj.happiness * 0.9) + (class_obj.wealth * 0.1)
        
        # 财富自然变化
        class_obj.wealth = max(0, min(1, class_obj.wealth + random.uniform(-0.01, 0.01)))
        
        # 教育随时间缓慢提高
        class_obj.education = min(1, class_obj.education + 0.002)
    
    db.commit() 