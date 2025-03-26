from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Any

from app.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserOut, UserUpdate, UserWithCharacters, Token
from app.core.security import authenticate_user, create_access_token, get_password_hash, get_current_user
from app.models.character import Character

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册
    
    Args:
        user: 用户注册信息
        db: 数据库会话
        
    Returns:
        新创建的用户信息
        
    Raises:
        HTTPException: 如果用户邮箱已被注册
    """
    # 检查邮箱是否已存在
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="此邮箱已注册")
    
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="此用户名已被使用")
    
    # 创建新用户
    try:
        hashed_password = get_password_hash(user.password)
        new_user = User(
            username=user.username, 
            email=user.email, 
            hashed_password=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="注册失败，请稍后再试")

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录
    
    Args:
        form_data: OAuth2表单数据，包含username和password字段
        db: 数据库会话
        
    Returns:
        访问令牌和令牌类型
        
    Raises:
        HTTPException: 如果验证失败
    """
    # 处理两种登录方式：用户名或邮箱
    user = None
    if "@" in form_data.username:  # 邮箱登录
        user = authenticate_user(db, form_data.username, form_data.password)
    else:  # 用户名登录
        db_user = db.query(User).filter(User.username == form_data.username).first()
        if db_user:
            user = authenticate_user(db, db_user.email, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token = create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前已认证的用户
        
    Returns:
        当前用户信息
    """
    return current_user

@router.put("/me", response_model=UserOut)
def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息
    
    Args:
        user_update: 待更新的用户信息
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        更新后的用户信息
    """
    # 如果修改了邮箱，需要检查是否已存在
    if user_update.email and user_update.email != current_user.email:
        if db.query(User).filter(User.email == user_update.email).first():
            raise HTTPException(status_code=400, detail="此邮箱已被使用")
        current_user.email = user_update.email
    
    # 如果修改了用户名，需要检查是否已存在
    if user_update.username and user_update.username != current_user.username:
        if db.query(User).filter(User.username == user_update.username).first():
            raise HTTPException(status_code=400, detail="此用户名已被使用")
        current_user.username = user_update.username
    
    # 如果修改了密码
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/me/characters", response_model=UserWithCharacters)
def get_user_characters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的所有角色
    
    Args:
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        用户信息和关联的角色列表
    """
    characters = db.query(Character).filter(Character.user_id == current_user.id).all()
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "characters": characters
    }

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除当前用户账号
    
    Args:
        current_user: 当前已认证的用户
        db: 数据库会话
    """
    db.delete(current_user)
    db.commit()
    return {"detail": "用户账号已删除"} 