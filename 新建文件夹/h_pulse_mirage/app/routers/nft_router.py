import hashlib, uuid, json
from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.fate_nft import FateNFT, NFTTransaction, NFTCollection, NFTCollectionItem
from app.engine.drama_builder import generate_fate_theater
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.character import Character
from app.config import settings

router = APIRouter()

@router.post("/mint", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def mint_fate_nft(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    铸造命运NFT
    
    将命运事件生成NFT数字资产
    
    Args:
        event_id: 事件ID
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        新铸造的NFT信息
        
    Raises:
        HTTPException: 如果铸造失败
    """
    # 获取事件剧本
    script = generate_fate_theater(event_id, db)
    if "error" in script:
        raise HTTPException(status_code=400, detail=script["error"])
    
    # 获取关联角色信息（用于获取八字信息）
    character_id = None
    try:
        character_id = script["nodes"][0]["character_id"]
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise ValueError("无法获取角色信息")
    except:
        raise HTTPException(status_code=400, detail="无法从剧本中获取角色信息")
    
    # 检查用户权限（是否为角色所有者）
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能为自己的角色铸造NFT")
    
    # 生成剧本哈希
    hash_algorithm = getattr(hashlib, settings.NFT_HASH_ALGORITHM)
    hash_str = hash_algorithm(json.dumps(script, ensure_ascii=False).encode("utf-8")).hexdigest()
    
    # 生成唯一NFT编号
    token_id = f"{settings.NFT_PREFIX}{uuid.uuid4().hex[:6]}"
    
    # 生成NFT标题和描述
    title = f"{character.name}的命运剧场：{script['title'].replace('命运剧场：', '')}" if "title" in script else f"{character.name}的命运记忆"
    
    # 生成事件标签
    tags = extract_tags_from_script(script)
    
    # 计算稀有度
    rarity_score = calculate_rarity_score(script)
    rarity = get_rarity_tier(rarity_score)
    
    # 从角色获取八字信息
    bazi_info = ""
    if character.bazi_summary and "八字" in character.bazi_summary:
        bazi_info = " ".join([f"{k}{v}" for k, v in character.bazi_summary["八字"].items()])
    
    try:
        # 创建新NFT
        new_nft = FateNFT(
            token_id=token_id,
            owner_id=current_user.id,
            title=title,
            bazi=bazi_info,
            data=script,
            narrative=f"{character.name}的命运记忆",
            visual_hash=hash_str,
            rarity=rarity,
            rarity_score=rarity_score,
            event_count=len(script.get("scenes", [])),
            tags=tags
        )
        db.add(new_nft)
        db.commit()
        db.refresh(new_nft)
        
        return {
            "token_id": token_id,
            "title": title,
            "hash": hash_str,
            "rarity": rarity,
            "rarity_score": rarity_score,
            "message": "NFT铸造成功"
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="NFT铸造失败，请稍后再试")

@router.get("/collection", response_model=List[Dict[str, Any]])
def get_user_nfts(
    skip: int = 0,
    limit: int = 20,
    on_sale: Optional[bool] = None,
    rarity: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的NFT收藏
    
    Args:
        skip: 分页偏移量
        limit: 分页大小
        on_sale: 是否在售
        rarity: 按稀有度筛选
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        NFT收藏列表
    """
    query = db.query(FateNFT).filter(FateNFT.owner_id == current_user.id)
    
    if on_sale is not None:
        query = query.filter(FateNFT.is_on_sale == on_sale)
    
    if rarity:
        query = query.filter(FateNFT.rarity == rarity)
    
    nfts = query.order_by(FateNFT.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "token_id": nft.token_id,
            "title": nft.title,
            "rarity": nft.rarity,
            "rarity_score": nft.rarity_score,
            "event_count": nft.event_count,
            "created_at": nft.created_at,
            "tags": nft.tags,
            "price": nft.price if nft.is_on_sale else None,
            "is_on_sale": nft.is_on_sale
        } for nft in nfts
    ]

@router.get("/market", response_model=List[Dict[str, Any]])
def get_nft_market(
    skip: int = 0,
    limit: int = 20,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    rarity: Optional[str] = None,
    sort_by: str = "price",
    db: Session = Depends(get_db)
):
    """
    浏览NFT市场
    
    Args:
        skip: 分页偏移量
        limit: 分页大小
        min_price: 最低价格
        max_price: 最高价格
        rarity: 按稀有度筛选
        sort_by: 排序方式(price, rarity_score, created_at)
        db: 数据库会话
        
    Returns:
        市场上的NFT列表
    """
    query = db.query(FateNFT).filter(FateNFT.is_on_sale == True)
    
    if min_price is not None:
        query = query.filter(FateNFT.price >= min_price)
    
    if max_price is not None:
        query = query.filter(FateNFT.price <= max_price)
    
    if rarity:
        query = query.filter(FateNFT.rarity == rarity)
    
    # 排序
    if sort_by == "price":
        query = query.order_by(FateNFT.price.asc())
    elif sort_by == "rarity_score":
        query = query.order_by(FateNFT.rarity_score.desc())
    elif sort_by == "created_at":
        query = query.order_by(FateNFT.created_at.desc())
    
    nfts = query.offset(skip).limit(limit).all()
    
    return [
        {
            "token_id": nft.token_id,
            "title": nft.title,
            "rarity": nft.rarity,
            "rarity_score": nft.rarity_score,
            "price": nft.price,
            "owner_id": nft.owner_id,
            "created_at": nft.created_at,
            "tags": nft.tags
        } for nft in nfts
    ]

@router.get("/{token_id}", response_model=Dict[str, Any])
def get_nft_details(
    token_id: str = Path(..., description="NFT的唯一标识"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取NFT详情
    
    Args:
        token_id: NFT唯一标识
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        NFT详情
        
    Raises:
        HTTPException: 如果NFT不存在
    """
    nft = db.query(FateNFT).filter(FateNFT.token_id == token_id).first()
    if not nft:
        raise HTTPException(status_code=404, detail="NFT不存在")
    
    # 更新查看次数
    nft.view_count += 1
    db.commit()
    
    # 获取所有者信息
    owner = db.query(User).filter(User.id == nft.owner_id).first()
    owner_name = owner.username if owner else "未知"
    
    # 获取交易历史
    transactions = db.query(NFTTransaction).filter(NFTTransaction.nft_id == nft.id).order_by(NFTTransaction.transaction_date.desc()).all()
    transaction_history = [
        {
            "date": t.transaction_date,
            "price": t.price,
            "seller_id": t.seller_id,
            "buyer_id": t.buyer_id
        } for t in transactions
    ]
    
    # 组合返回信息
    return {
        "token_id": nft.token_id,
        "title": nft.title,
        "narrative": nft.narrative,
        "bazi": nft.bazi,
        "owner": owner_name,
        "owner_id": nft.owner_id,
        "created_at": nft.created_at,
        "rarity": nft.rarity,
        "rarity_score": nft.rarity_score,
        "visual_hash": nft.visual_hash,
        "is_on_sale": nft.is_on_sale,
        "price": nft.price if nft.is_on_sale else None,
        "event_count": nft.event_count,
        "view_count": nft.view_count,
        "like_count": nft.like_count,
        "tags": nft.tags,
        "data": nft.data,  # 完整剧本数据
        "transaction_history": transaction_history,
        "is_owner": nft.owner_id == current_user.id
    }

@router.put("/{token_id}/price", response_model=Dict[str, Any])
def update_nft_price(
    token_id: str,
    price: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新NFT价格
    
    Args:
        token_id: NFT唯一标识
        price: 新价格
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        更新结果
        
    Raises:
        HTTPException: 如果NFT不存在或无权更新
    """
    nft = db.query(FateNFT).filter(FateNFT.token_id == token_id).first()
    if not nft:
        raise HTTPException(status_code=404, detail="NFT不存在")
    
    # 只有所有者可以更新价格
    if nft.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="只有NFT所有者才能设置价格")
    
    if price < 0:
        raise HTTPException(status_code=400, detail="价格不能为负数")
    
    # 更新价格并设置为在售状态
    nft.price = price
    nft.is_on_sale = price > 0
    
    db.commit()
    
    return {
        "token_id": token_id,
        "price": price,
        "is_on_sale": nft.is_on_sale,
        "message": "价格更新成功"
    }

@router.post("/{token_id}/buy", response_model=Dict[str, Any])
def buy_nft(
    token_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    购买NFT
    
    Args:
        token_id: NFT唯一标识
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        购买结果
        
    Raises:
        HTTPException: 如果购买失败
    """
    nft = db.query(FateNFT).filter(FateNFT.token_id == token_id).first()
    if not nft:
        raise HTTPException(status_code=404, detail="NFT不存在")
    
    # 检查是否在售
    if not nft.is_on_sale:
        raise HTTPException(status_code=400, detail="此NFT不在售")
    
    # 不能购买自己的NFT
    if nft.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能购买自己的NFT")
    
    # 记录价格和卖家
    price = nft.price
    seller_id = nft.owner_id
    
    try:
        # 记录交易
        transaction = NFTTransaction(
            nft_id=nft.id,
            seller_id=seller_id,
            buyer_id=current_user.id,
            price=price,
            transaction_hash=f"tx_{uuid.uuid4().hex}"
        )
        db.add(transaction)
        
        # 更新NFT所有权
        nft.owner_id = current_user.id
        nft.is_on_sale = False
        nft.transaction_history.append({
            "date": datetime.utcnow().isoformat(),
            "price": price,
            "seller_id": seller_id,
            "buyer_id": current_user.id
        })
        
        db.commit()
        
        return {
            "token_id": token_id,
            "price": price,
            "seller_id": seller_id,
            "buyer_id": current_user.id,
            "transaction_hash": transaction.transaction_hash,
            "message": "NFT购买成功"
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="交易失败，请稍后再试")

@router.post("/collections", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def create_collection(
    name: str,
    description: Optional[str] = None,
    is_public: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建NFT收藏集
    
    Args:
        name: 收藏集名称
        description: 收藏集描述
        is_public: 是否公开
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        新创建的收藏集
        
    Raises:
        HTTPException: 如果创建失败
    """
    try:
        collection = NFTCollection(
            owner_id=current_user.id,
            name=name,
            description=description,
            is_public=is_public
        )
        db.add(collection)
        db.commit()
        db.refresh(collection)
        
        return {
            "id": collection.id,
            "name": collection.name,
            "is_public": collection.is_public,
            "message": "收藏集创建成功"
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="收藏集创建失败，请稍后再试")

@router.post("/{token_id}/like", response_model=Dict[str, Any])
def like_nft(
    token_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    点赞NFT
    
    Args:
        token_id: NFT唯一标识
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        点赞结果
    """
    nft = db.query(FateNFT).filter(FateNFT.token_id == token_id).first()
    if not nft:
        raise HTTPException(status_code=404, detail="NFT不存在")
    
    # 增加喜欢计数
    nft.like_count += 1
    db.commit()
    
    return {
        "token_id": token_id,
        "like_count": nft.like_count,
        "message": "点赞成功"
    }

# 辅助函数
def extract_tags_from_script(script: Dict[str, Any]) -> List[str]:
    """从剧本中提取标签"""
    tags = []
    
    # 从剧本标题中提取关键词
    if "title" in script:
        title_words = script["title"].split()
        for word in title_words:
            if len(word) > 1 and word not in ["的", "命运", "剧场"]:
                tags.append(word)
    
    # 从剧情中提取关键事件
    if "scenes" in script:
        for scene in script["scenes"]:
            if "action" in scene:
                action = scene["action"]
                if action in ["背叛", "冲突", "决战", "拯救", "牺牲", "冒险", "发现"]:
                    if action not in tags:
                        tags.append(action)
    
    # 限制标签数量
    return tags[:5]

def calculate_rarity_score(script: Dict[str, Any]) -> float:
    """计算NFT稀有度评分"""
    # 基础分值
    score = 50.0
    
    # 场景数量影响
    scene_count = len(script.get("scenes", []))
    if scene_count > 10:
        score += 10
    elif scene_count > 5:
        score += 5
    
    # 剧情转折点
    twist_keywords = ["背叛", "牺牲", "惊变", "灾难", "奇迹", "命运", "转折"]
    twist_count = 0
    
    for scene in script.get("scenes", []):
        scene_text = json.dumps(scene, ensure_ascii=False)
        for keyword in twist_keywords:
            if keyword in scene_text:
                twist_count += 1
                break
    
    # 转折点增加稀有度
    score += twist_count * 5
    
    # 添加随机波动（保持稀有度分布）
    import random
    score += random.uniform(-3, 3)
    
    # 限制评分范围
    return max(0, min(100, score))

def get_rarity_tier(score: float) -> str:
    """根据稀有度评分确定等级"""
    if score >= 90:
        return "传说"
    elif score >= 75:
        return "史诗"
    elif score >= 50:
        return "稀有"
    else:
        return "普通" 