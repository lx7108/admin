from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class DestinyNode(Base):
    __tablename__ = "destiny_nodes"
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    event_name = Column(String(200), nullable=False)
    event_type = Column(String(50))   # 情感 / 社会 / 决策 / 健康 / 命理
    decision = Column(String(200))
    result = Column(String(200))
    consequence = Column(JSON)        # 对属性/状态的影响
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # 新增字段
    description = Column(Text, nullable=True)
    impact_level = Column(Float, default=1.0)  # 事件影响程度 1-10
    is_critical = Column(Boolean, default=False)  # 是否关键转折点
    parent_id = Column(Integer, ForeignKey("destiny_nodes.id"), nullable=True)  # 父节点
    probability = Column(Float, default=1.0)  # 事件发生概率 0-1
    importance_score = Column(Float, default=0)  # 命运重要性评分
    tags = Column(JSON, default=[])  # 事件标签
    
    # 关系定义
    character = relationship("Character", back_populates="destiny_nodes")
    parent = relationship("DestinyNode", remote_side=[id], backref="children")
    
    def is_leaf(self):
        """是否为叶子节点（无子节点）"""
        return len(self.children) == 0
    
    def is_root(self):
        """是否为根节点（无父节点）"""
        return self.parent_id is None
    
    def __repr__(self):
        return f"<DestinyNode {self.event_name} ({self.id})>" 