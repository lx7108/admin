from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class FateNFT(Base):
    """命运NFT模型"""
    __tablename__ = "fate_nfts"
    id = Column(Integer, primary_key=True)
    token_id = Column(String(50), unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    bazi = Column(String(50))  # 八字信息（简化）
    data = Column(JSON, nullable=False)  # 完整剧本数据
    narrative = Column(Text)  # 故事概要
    visual_hash = Column(String(64), nullable=False)  # 哈希值用于内容唯一性
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 新增字段
    price = Column(Float, nullable=True)  # 当前挂售价格（如果在出售）
    is_on_sale = Column(Boolean, default=False)  # 是否在出售中
    rarity = Column(String(20), default="普通")  # 稀有度：普通/稀有/史诗/传说
    rarity_score = Column(Float, default=0.0)  # 稀有度评分
    generation = Column(Integer, default=1)  # NFT生成代次
    event_count = Column(Integer, default=0)  # 包含事件数量
    tags = Column(JSON, default=[])  # NFT标签
    view_count = Column(Integer, default=0)  # 查看次数
    like_count = Column(Integer, default=0)  # 喜欢数量
    transaction_history = Column(JSON, default=[])  # 交易历史
    
    # 关系定义
    owner = relationship("User", back_populates="fate_nfts")
    
    def __repr__(self):
        return f"<FateNFT {self.title} ({self.token_id})>"

class NFTTransaction(Base):
    """NFT交易记录模型"""
    __tablename__ = "nft_transactions"
    id = Column(Integer, primary_key=True)
    nft_id = Column(Integer, ForeignKey("fate_nfts.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    price = Column(Float, nullable=False)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    transaction_hash = Column(String(64), unique=True)  # 交易哈希
    
    # 关系定义
    nft = relationship("FateNFT")
    seller = relationship("User", foreign_keys=[seller_id])
    buyer = relationship("User", foreign_keys=[buyer_id])
    
    def __repr__(self):
        return f"<NFTTransaction NFT:{self.nft_id} {self.seller_id}->{self.buyer_id} ¥{self.price}>"

class NFTCollection(Base):
    """NFT收藏集模型"""
    __tablename__ = "nft_collections"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    cover_url = Column(String(255), nullable=True)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系定义
    owner = relationship("User")
    items = relationship("NFTCollectionItem", back_populates="collection", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<NFTCollection {self.name} (Owner:{self.owner_id})>"

class NFTCollectionItem(Base):
    """NFT收藏物品关联模型"""
    __tablename__ = "nft_collection_items"
    id = Column(Integer, primary_key=True)
    collection_id = Column(Integer, ForeignKey("nft_collections.id"), nullable=False)
    nft_id = Column(Integer, ForeignKey("fate_nfts.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # 关系定义
    collection = relationship("NFTCollection", back_populates="items")
    nft = relationship("FateNFT")
    
    def __repr__(self):
        return f"<NFTCollectionItem Col:{self.collection_id} NFT:{self.nft_id}>" 