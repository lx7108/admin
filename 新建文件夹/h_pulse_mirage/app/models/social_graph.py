from sqlalchemy import Column, Integer, Float, ForeignKey, String, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Relationship(Base):
    __tablename__ = "relationships"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    relation_type = Column(String(50), nullable=False)  # 朋友 / 情人 / 敌人 / 合作伙伴
    trust = Column(Float, default=0.5)  # 信任程度 0-1
    conflict = Column(Float, default=0.0)  # 冲突程度 0-1
    
    # 新增字段
    started_at = Column(DateTime, default=datetime.utcnow)  # 关系开始时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 最后更新时间
    ended_at = Column(DateTime, nullable=True)  # 关系结束时间
    is_active = Column(Boolean, default=True)  # 关系是否有效
    intensity = Column(Float, default=0.5)  # 关系强度 0-1
    history = Column(JSON, default=[])  # 关系历史记录
    influence = Column(Float, default=0.0)  # 影响力 -1到1，负为负面影响
    tags = Column(JSON, default=[])  # 关系标签
    
    # 关系定义
    source = relationship("Character", foreign_keys=[source_id], back_populates="relationships_source")
    target = relationship("Character", foreign_keys=[target_id], back_populates="relationships_target")
    
    def is_mutual(self, db):
        """检查是否为双向关系"""
        reverse = db.query(Relationship).filter(
            Relationship.source_id == self.target_id,
            Relationship.target_id == self.source_id,
            Relationship.relation_type == self.relation_type
        ).first()
        return reverse is not None
    
    def __repr__(self):
        return f"<Relationship {self.relation_type} ({self.source_id} -> {self.target_id})>"

class SocialInteraction(Base):
    """社交互动记录"""
    __tablename__ = "social_interactions"
    id = Column(Integer, primary_key=True)
    relationship_id = Column(Integer, ForeignKey("relationships.id"), nullable=False)
    causal_event_id = Column(Integer, ForeignKey("causal_events.id"), nullable=True)
    interaction_type = Column(String(50), nullable=False)  # 交谈、帮助、冲突等
    description = Column(String(255))
    impact = Column(Float)  # 正负值表示积极或消极影响
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # 关系定义
    relationship = relationship("Relationship", backref="interactions")
    causal_event = relationship("CausalEvent") 