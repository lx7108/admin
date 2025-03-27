from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Float, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class CausalEvent(Base):
    __tablename__ = "causal_events"
    id = Column(Integer, primary_key=True)
    actor_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("characters.id"), nullable=True)
    action = Column(String(200), nullable=False)
    context = Column(JSON, default={})
    result = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.utcnow)
    origin_event = Column(Integer, ForeignKey("causal_events.id"), nullable=True)
    
    # 新增字段
    description = Column(Text, nullable=True)
    impact_score = Column(Float, default=0.0)  # 影响分数
    emotion_impact = Column(JSON, default={})  # 情感影响 {"joy": 0.1, "anger": -0.2, ...}
    social_impact = Column(JSON, default={})  # 社会关系影响
    is_public = Column(Boolean, default=True)  # 是否公开事件
    tags = Column(JSON, default=[])  # 事件标签
    duration = Column(Integer, default=0)  # 持续时间（小时）
    location = Column(String(100), nullable=True)  # 事件发生地点
    
    # 关系定义
    actor = relationship("Character", foreign_keys=[actor_id], back_populates="causal_events_actor")
    target = relationship("Character", foreign_keys=[target_id], back_populates="causal_events_target")
    parent_event = relationship("CausalEvent", remote_side=[id], backref="child_events")
    
    def get_path_to_root(self):
        """获取到根事件的路径"""
        path = [self]
        current = self
        while current.origin_event:
            parent = current.parent_event
            if parent:
                path.append(parent)
                current = parent
            else:
                break
        return list(reversed(path))
    
    def __repr__(self):
        actor_str = f"角色#{self.actor_id}"
        target_str = f" -> 角色#{self.target_id}" if self.target_id else ""
        return f"<CausalEvent {self.action} ({actor_str}{target_str})>" 