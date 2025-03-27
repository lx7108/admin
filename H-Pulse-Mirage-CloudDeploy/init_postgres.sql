-- 创建数据库与用户
CREATE DATABASE mirage_db;
CREATE USER mirage_user WITH PASSWORD 'mirage_pass';
GRANT ALL PRIVILEGES ON DATABASE mirage_db TO mirage_user;