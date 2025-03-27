from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Any
from datetime import datetime

# 基础用户模型
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

# 创建用户请求模型
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('用户名必须是字母或数字')
        return v

# 更新用户请求模型
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if v is not None and not v.isalnum():
            raise ValueError('用户名必须是字母或数字')
        return v

# 用户响应模型
class UserOut(UserBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "username": "testuser",
                "email": "user@example.com",
                "created_at": "2025-03-26T10:00:00"
            }
        }

# 用户身份验证响应模型
class Token(BaseModel):
    access_token: str
    token_type: str
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }

# 令牌数据模型
class TokenData(BaseModel):
    user_id: Optional[int] = None

# 用户带角色模型
class UserWithCharacters(UserOut):
    characters: List[Any] = []
    
    class Config:
        orm_mode = True 