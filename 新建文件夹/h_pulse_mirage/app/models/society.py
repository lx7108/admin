from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Regime(Base):
    """政权系统模型"""
    __tablename__ = "regimes"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # 民主/寡头/AI极权
    satisfaction = Column(Float, default=0.5)  # 民众满意度 0-1
    corruption = Column(Float, default=0.2)  # 腐败程度 0-1
    stability = Column(Float, default=0.5)  # 稳定性 0-1
    prosperity = Column(Float, default=0.5)  # 繁荣程度 0-1
    freedom = Column(Float, default=0.5)  # 自由度 0-1
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)
    
    # 新增字段
    policies = Column(JSON, default=[])  # 政策列表
    events = Column(JSON, default=[])  # 重大事件记录
    leaders = Column(JSON, default=[])  # 领导人记录
    tech_level = Column(Float, default=0.5)  # 科技水平 0-1
    
    # 关系定义
    social_classes = relationship("SocialClass", back_populates="regime")
    
    def __repr__(self):
        return f"<Regime {self.name} ({self.type})>"

class SocialClass(Base):
    """社会阶层模型"""
    __tablename__ = "social_classes"
    id = Column(Integer, primary_key=True)
    regime_id = Column(Integer, ForeignKey("regimes.id"), nullable=False)
    name = Column(String(50), nullable=False)  # 统治/中产/底层
    wealth = Column(Float, default=0.5)  # 财富水平 0-1
    population_ratio = Column(Float, default=0.33)  # 人口比例 0-1
    
    # 新增字段
    influence = Column(Float, default=0.5)  # 影响力 0-1
    education = Column(Float, default=0.5)  # 教育水平 0-1
    health = Column(Float, default=0.5)  # 健康水平 0-1
    happiness = Column(Float, default=0.5)  # 幸福感 0-1
    mobility = Column(Float, default=0.2)  # 流动性 0-1
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系定义
    regime = relationship("Regime", back_populates="social_classes")
    
    def __repr__(self):
        return f"<SocialClass {self.name} (占比{self.population_ratio:.1%})>"

class SocialEvent(Base):
    """社会事件模型"""
    __tablename__ = "social_events"
    id = Column(Integer, primary_key=True)
    regime_id = Column(Integer, ForeignKey("regimes.id"), nullable=False)
    name = Column(String(100), nullable=False)
    event_type = Column(String(50), nullable=False)  # 革命、改革、战争、灾难等
    description = Column(Text, nullable=True)
    impact = Column(JSON, default={})  # 对各项指标的影响
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration = Column(Integer, default=0)  # 持续时间（天）
    is_active = Column(Boolean, default=True)  # 事件是否仍在进行
    
    # 关系定义
    regime = relationship("Regime")
    affected_classes = relationship("SocialClassEvent", back_populates="event")
    
    def __repr__(self):
        return f"<SocialEvent {self.name} ({self.event_type})>"

class SocialClassEvent(Base):
    """阶层事件影响关联模型"""
    __tablename__ = "social_class_events"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("social_events.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("social_classes.id"), nullable=False)
    impact = Column(Float)  # 影响程度 -1到1
    
    # 关系定义
    event = relationship("SocialEvent", back_populates="affected_classes")
    social_class = relationship("SocialClass") 