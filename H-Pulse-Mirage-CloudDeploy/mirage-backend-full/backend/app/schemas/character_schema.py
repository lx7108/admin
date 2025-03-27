from pydantic import BaseModel, validator, Field
from typing import Optional, Dict, List, Any
from datetime import datetime

# 基础角色模型
class CharacterBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    birth_time: str = Field(..., description="出生时间，格式：YYYY-MM-DD HH:MM")
    
    @validator('birth_time')
    def validate_birth_time(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("出生时间格式必须为 YYYY-MM-DD HH:MM")
        return v

# 创建角色请求模型
class CharacterCreate(CharacterBase):
    user_id: int
    background_story: Optional[str] = Field(None, max_length=2000)
    avatar_url: Optional[str] = None

# 更新角色请求模型
class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    background_story: Optional[str] = Field(None, max_length=2000)
    avatar_url: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    personality: Optional[Dict[str, float]] = None
    
    @validator('personality')
    def validate_personality(cls, v):
        if v:
            required_traits = ["O", "C", "E", "A", "N"]
            for trait in required_traits:
                if trait not in v:
                    raise ValueError(f"人格特质必须包含 {trait}")
                if not 0 <= v[trait] <= 1:
                    raise ValueError(f"人格特质值必须在0-1之间")
        return v

# 角色响应模型
class CharacterOut(CharacterBase):
    id: int
    user_id: int
    attributes: Dict[str, Any]
    personality: Dict[str, float]
    fate_score: float
    created_at: Optional[datetime] = None
    avatar_url: Optional[str] = None
    background_story: Optional[str] = None
    bazi_summary: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "name": "林澈",
                "birth_time": "1997-07-16 11:50",
                "attributes": {
                    "physique": 7,
                    "intelligence": 8,
                    "emotion": 6,
                    "social": 5
                },
                "personality": {
                    "O": 0.7,
                    "C": 0.6,
                    "E": 0.4,
                    "A": 0.5,
                    "N": 0.3
                },
                "fate_score": 65.5,
                "bazi_summary": {
                    "八字": "丁丑 丁未 己未 庚午",
                    "五行": {"木": 2, "火": 3, "土": 3, "金": 1, "水": 1}
                }
            }
        }

# 角色列表响应模型（精简信息）
class CharacterBrief(BaseModel):
    id: int
    name: str
    fate_score: float
    avatar_url: Optional[str] = None
    
    class Config:
        orm_mode = True

# 角色带命运事件响应模型
class CharacterWithEvents(CharacterOut):
    destiny_nodes: List[Any] = []
    
    class Config:
        orm_mode = True

# 角色带社会关系响应模型
class CharacterWithRelationships(CharacterOut):
    relationships: List[Any] = []
    
    class Config:
        orm_mode = True

# 角色模拟结果模型
class CharacterSimulation(BaseModel):
    character_id: int
    name: str
    actions: List[Dict[str, Any]]
    fate_delta: float
    
    class Config:
        schema_extra = {
            "example": {
                "character_id": 1,
                "name": "林澈",
                "actions": [
                    {"step": 0, "action": "合作", "reward": 1.2},
                    {"step": 1, "action": "欺骗", "reward": 0.8}
                ],
                "fate_delta": 2.0
            }
        } 