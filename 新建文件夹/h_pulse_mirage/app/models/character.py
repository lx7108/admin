from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), index=True, nullable=False)
    birth_time = Column(String(50), nullable=False)
    destiny_tree = Column(JSON, default={})
    attributes = Column(JSON)       # 体魄、智力、情感等
    personality = Column(JSON)      # 大五人格
    fate_score = Column(Float, default=0.0)
    
    # 新增字段
    avatar_url = Column(String(255), nullable=True)
    background_story = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = Column(Boolean, default=False)
    last_simulation_date = Column(DateTime, nullable=True)
    bazi_summary = Column(JSON, default={})  # 八字命盘分析摘要
    
    # 关系定义
    user = relationship("User", back_populates="characters")
    destiny_nodes = relationship("DestinyNode", back_populates="character", cascade="all, delete-orphan")
    causal_events_actor = relationship("CausalEvent", foreign_keys="CausalEvent.actor_id", back_populates="actor", cascade="all, delete-orphan")
    causal_events_target = relationship("CausalEvent", foreign_keys="CausalEvent.target_id", back_populates="target")
    relationships_source = relationship("Relationship", foreign_keys="Relationship.source_id", back_populates="source", cascade="all, delete-orphan")
    relationships_target = relationship("Relationship", foreign_keys="Relationship.target_id", back_populates="target")
    
    def to_profile(self):
        """转换为AI模拟用的配置文件格式"""
        return {
            "id": self.id,
            "name": self.name,
            "O": self.personality.get("O", 0.5),
            "C": self.personality.get("C", 0.5),
            "E": self.personality.get("E", 0.5),
            "A": self.personality.get("A", 0.5),
            "N": self.personality.get("N", 0.5),
            "wuxing": self.attributes.get("wuxing", {}),
            "emotion_state": {
                "joy": 0.25,
                "anger": 0.25,
                "sadness": 0.25, 
                "fear": 0.25
            },
            "reputation": 0.5,
            "trust": 0.5,
            "wealth": 0.5,
            "status": 0.5,
            # 添加额外属性
            "background": self.background_story,
            "bazi_summary": self.bazi_summary
        }
    
    def __repr__(self):
        return f"<Character {self.name} ({self.id})>" 