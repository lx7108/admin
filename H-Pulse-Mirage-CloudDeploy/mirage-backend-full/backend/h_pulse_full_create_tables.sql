
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE
);
COMMENT ON TABLE users IS '系统用户表，记录基本身份与权限信息';
COMMENT ON COLUMN users.username IS '用户名，唯一';
COMMENT ON COLUMN users.email IS '用户邮箱，唯一';


-- 角色表
CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    birth_time VARCHAR(50) NOT NULL,
    destiny_tree JSON NOT NULL DEFAULT '{}',
    attributes JSON,
    personality JSON,
    fate_score FLOAT NOT NULL DEFAULT 0.0,
    avatar_url VARCHAR(255),
    background_story TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN NOT NULL DEFAULT FALSE,
    last_simulation_date TIMESTAMP,
    bazi_summary JSON NOT NULL DEFAULT '{}'
);
COMMENT ON TABLE characters IS '虚拟人物角色表，记录用户创建的角色及其命理、性格、关系等';


-- 命运节点表
CREATE TABLE destiny_nodes (
    id SERIAL PRIMARY KEY,
    character_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    event_name VARCHAR(200) NOT NULL,
    event_type VARCHAR(50),
    decision VARCHAR(200),
    result VARCHAR(200),
    consequence JSON,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    impact_level FLOAT NOT NULL DEFAULT 1.0,
    is_critical BOOLEAN NOT NULL DEFAULT FALSE,
    parent_id INTEGER REFERENCES destiny_nodes(id) ON DELETE SET NULL,
    probability FLOAT NOT NULL DEFAULT 1.0,
    importance_score FLOAT NOT NULL DEFAULT 0,
    tags JSON NOT NULL DEFAULT '[]'
);
COMMENT ON TABLE destiny_nodes IS '角色命运节点表，记录事件链及其因果结构';


-- 因果事件表
CREATE TABLE causal_events (
    id SERIAL PRIMARY KEY,
    actor_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    target_id INTEGER REFERENCES characters(id) ON DELETE SET NULL,
    action VARCHAR(200) NOT NULL,
    context JSON NOT NULL DEFAULT '{}',
    result JSON NOT NULL DEFAULT '{}',
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    origin_event INTEGER REFERENCES causal_events(id) ON DELETE SET NULL,
    description TEXT,
    impact_score FLOAT NOT NULL DEFAULT 0.0,
    emotion_impact JSON NOT NULL DEFAULT '{}',
    social_impact JSON NOT NULL DEFAULT '{}',
    is_public BOOLEAN NOT NULL DEFAULT TRUE,
    tags JSON NOT NULL DEFAULT '[]',
    duration INTEGER NOT NULL DEFAULT 0,
    location VARCHAR(100)
);
COMMENT ON TABLE causal_events IS '角色之间因果互动事件记录，用于行为链建模与模拟';


-- 命运NFT表
CREATE TABLE fate_nfts (
    id SERIAL PRIMARY KEY,
    token_id VARCHAR(50) UNIQUE NOT NULL,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    bazi VARCHAR(50),
    data JSON NOT NULL,
    narrative TEXT,
    visual_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price FLOAT,
    is_on_sale BOOLEAN NOT NULL DEFAULT FALSE,
    rarity VARCHAR(20) NOT NULL DEFAULT '普通',
    rarity_score FLOAT NOT NULL DEFAULT 0.0,
    generation INTEGER NOT NULL DEFAULT 1,
    event_count INTEGER NOT NULL DEFAULT 0,
    tags JSON NOT NULL DEFAULT '[]',
    view_count INTEGER NOT NULL DEFAULT 0,
    like_count INTEGER NOT NULL DEFAULT 0,
    transaction_history JSON NOT NULL DEFAULT '[]'
);


-- NFT交易表
CREATE TABLE nft_transactions (
    id SERIAL PRIMARY KEY,
    nft_id INTEGER NOT NULL REFERENCES fate_nfts(id) ON DELETE CASCADE,
    seller_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    buyer_id INTEGER NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    price FLOAT NOT NULL,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transaction_hash VARCHAR(64) UNIQUE NOT NULL
);


-- NFT收藏夹表
CREATE TABLE nft_collections (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    cover_url VARCHAR(255),
    is_public BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- NFT收藏夹项
CREATE TABLE nft_collection_items (
    id SERIAL PRIMARY KEY,
    collection_id INTEGER NOT NULL REFERENCES nft_collections(id) ON DELETE CASCADE,
    nft_id INTEGER NOT NULL REFERENCES fate_nfts(id) ON DELETE CASCADE,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);


-- 社交关系表
CREATE TABLE relationships (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    target_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    relation_type VARCHAR(50) NOT NULL,
    trust FLOAT NOT NULL DEFAULT 0.5,
    conflict FLOAT NOT NULL DEFAULT 0.0,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    intensity FLOAT NOT NULL DEFAULT 0.5,
    influence FLOAT NOT NULL DEFAULT 0.0,
    tags JSON NOT NULL DEFAULT '[]',
    history JSON NOT NULL DEFAULT '[]'
);


-- 社交互动记录表
CREATE TABLE social_interactions (
    id SERIAL PRIMARY KEY,
    relationship_id INTEGER NOT NULL REFERENCES relationships(id) ON DELETE CASCADE,
    causal_event_id INTEGER REFERENCES causal_events(id) ON DELETE SET NULL,
    interaction_type VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    impact FLOAT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- 政权系统表
CREATE TABLE regimes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    satisfaction FLOAT NOT NULL DEFAULT 0.5,
    corruption FLOAT NOT NULL DEFAULT 0.2,
    stability FLOAT NOT NULL DEFAULT 0.5,
    prosperity FLOAT NOT NULL DEFAULT 0.5,
    freedom FLOAT NOT NULL DEFAULT 0.5,
    description TEXT,
    policies JSON NOT NULL DEFAULT '[]',
    events JSON NOT NULL DEFAULT '[]',
    leaders JSON NOT NULL DEFAULT '[]',
    tech_level FLOAT NOT NULL DEFAULT 0.5,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN NOT NULL DEFAULT TRUE
);


-- 社会阶层表
CREATE TABLE social_classes (
    id SERIAL PRIMARY KEY,
    regime_id INTEGER NOT NULL REFERENCES regimes(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    wealth FLOAT NOT NULL DEFAULT 0.5,
    population_ratio FLOAT NOT NULL DEFAULT 0.33,
    influence FLOAT NOT NULL DEFAULT 0.5,
    education FLOAT NOT NULL DEFAULT 0.5,
    health FLOAT NOT NULL DEFAULT 0.5,
    happiness FLOAT NOT NULL DEFAULT 0.5,
    mobility FLOAT NOT NULL DEFAULT 0.2,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- 社会事件表
CREATE TABLE social_events (
    id SERIAL PRIMARY KEY,
    regime_id INTEGER NOT NULL REFERENCES regimes(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    description TEXT,
    impact JSON NOT NULL DEFAULT '{}',
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    duration INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);


-- 社会事件与阶层关系表
CREATE TABLE social_class_events (
    id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL REFERENCES social_events(id) ON DELETE CASCADE,
    class_id INTEGER NOT NULL REFERENCES social_classes(id) ON DELETE CASCADE,
    impact FLOAT NOT NULL
);
