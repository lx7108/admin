
-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 角色表
CREATE TABLE IF NOT EXISTS characters (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(50),
    gender VARCHAR(10),
    birth_year INTEGER,
    birth_month INTEGER,
    birth_day INTEGER,
    birth_hour INTEGER,
    bazi VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 命运模拟记录
CREATE TABLE IF NOT EXISTS fate_simulations (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id),
    start_age INTEGER,
    end_age INTEGER,
    result_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI 决策日志
CREATE TABLE IF NOT EXISTS ai_decisions (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id),
    age INTEGER,
    input_state JSONB,
    action_taken VARCHAR(50),
    reward FLOAT,
    next_state JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

    , email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 角色表
CREATE TABLE IF NOT EXISTS characters (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(50) NOT NULL,
    gender VARCHAR(10),
    birth_year INTEGER,
    birth_month INTEGER,
    birth_day INTEGER,
    birth_hour INTEGER,
    bazi VARCHAR(100),
    traits JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 命运轨迹表
CREATE TABLE IF NOT EXISTS destinies (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id),
    age INTEGER,
    year INTEGER,
    action VARCHAR(100),
    reward FLOAT,
    state JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI 决策日志表
CREATE TABLE IF NOT EXISTS decisions (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    state JSONB,
    action VARCHAR(100),
    reward FLOAT,
    next_state JSONB
);

-- 系统日志表
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    tag VARCHAR(100),
    message TEXT,
    level VARCHAR(10),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初始管理员
INSERT INTO users (username, hashed_password, email)
VALUES ('admin', 'admin_password_hash', 'admin@example.com')
ON CONFLICT DO NOTHING;
