
-- 初始化角色表（简化示例，可根据 h_pulse_full_create_tables.sql 拓展）
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, hashed_password, email)
VALUES ('admin', 'adminpasswordhash', 'admin@example.com')
ON CONFLICT DO NOTHING;
