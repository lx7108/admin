from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

# 基础命运节点模型
class DestinyNodeBase(BaseModel):
    character_id: int
    event_name: str = Field(..., min_length=2, max_length=200)
    event_type: str = Field(..., description="事件类型: 情感/社会/决策/健康/命理")
    
    @validator('event_type')
    def validate_event_type(cls, v):
        valid_types = ["情感", "社会", "决策", "健康", "命理"]
        if v not in valid_types:
            raise ValueError(f"事件类型必须为: {', '.join(valid_types)}")
        return v

# 创建命运事件请求模型
class DestinyInput(DestinyNodeBase):
    decision: str = Field(..., min_length=1, max_length=200)
    result: str = Field(..., min_length=1, max_length=200)
    consequence: Dict[str, Any] = Field(..., description="对属性/状态的影响")
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    parent_id: Optional[int] = None
    
    @validator('tags')
    def validate_tags(cls, v):
        if v:
            for tag in v:
                if not re.match(r'^[a-zA-Z0-9\u4e00-\u9fa5_]{1,20}$', tag):
                    raise ValueError(f"标签格式错误: {tag}")
            if len(v) > 5:
                raise ValueError("标签数量不能超过5个")
        return v

# 更新命运事件请求模型
class DestinyUpdate(BaseModel):
    event_name: Optional[str] = Field(None, min_length=2, max_length=200)
    decision: Optional[str] = Field(None, min_length=1, max_length=200)
    result: Optional[str] = Field(None, min_length=1, max_length=200)
    consequence: Optional[Dict[str, Any]] = None
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    is_critical: Optional[bool] = None
    impact_level: Optional[float] = Field(None, ge=1.0, le=10.0)
    
    @validator('impact_level')
    def validate_impact_level(cls, v):
        if v is not None and not (1.0 <= v <= 10.0):
            raise ValueError("影响程度必须在1.0到10.0之间")
        return v

# 命运事件响应模型
class DestinyOutput(DestinyNodeBase):
    id: int
    decision: str
    result: str
    consequence: Dict[str, Any]
    timestamp: datetime
    description: Optional[str] = None
    impact_level: Optional[float] = None
    is_critical: Optional[bool] = None
    importance_score: Optional[float] = None
    tags: Optional[List[str]] = None
    parent_id: Optional[int] = None
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "character_id": 1,
                "event_name": "复仇计划",
                "event_type": "决策",
                "decision": "执行",
                "result": "目标被暗杀",
                "consequence": {"emotion": 0.3, "trust": -0.5},
                "timestamp": "2025-03-26T12:00:00",
                "impact_level": 8.5,
                "is_critical": True,
                "tags": ["背叛", "黑暗"]
            }
        }

# 命运树节点列表响应模型
class DestinyTree(BaseModel):
    nodes: List[DestinyOutput]
    root_id: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "root_id": 1,
                "nodes": [
                    {
                        "id": 1,
                        "character_id": 1,
                        "event_name": "出生",
                        "event_type": "命理",
                        "decision": "降生",
                        "result": "进入世界",
                        "consequence": {"fate_score": 50},
                        "parent_id": None
                    },
                    {
                        "id": 2,
                        "character_id": 1,
                        "event_name": "求学之路",
                        "event_type": "决策",
                        "decision": "努力学习",
                        "result": "成绩优异",
                        "consequence": {"intelligence": 2},
                        "parent_id": 1
                    }
                ]
            }
        }

# 命运预测模型
class DestinyPrediction(BaseModel):
    based_on_event_id: int
    possible_paths: List[Dict[str, Any]]
    probability_factors: Dict[str, float]
    
    class Config:
        schema_extra = {
            "example": {
                "based_on_event_id": 5,
                "possible_paths": [
                    {
                        "event_name": "隐忍不发",
                        "probability": 0.7,
                        "consequence": {"reputation": 0.2, "anger": 0.5}
                    },
                    {
                        "event_name": "公开反抗",
                        "probability": 0.3,
                        "consequence": {"reputation": -0.3, "freedom": 0.6}
                    }
                ],
                "probability_factors": {
                    "personality": 0.4,
                    "past_decisions": 0.3,
                    "external_pressure": 0.3
                }
            }
        } 