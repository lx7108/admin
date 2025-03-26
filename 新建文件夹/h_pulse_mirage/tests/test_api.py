import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.core.security import get_password_hash

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建测试用户数据
test_user_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}

# 创建测试角色数据
test_character_data = {
    "user_id": 1,
    "name": "测试角色",
    "birth_time": "1997-07-16 11:50",
    "background_story": "这是一个测试角色的背景故事。"
}

@pytest.fixture
def test_db():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # 创建测试用户
    db = TestingSessionLocal()
    from app.models.user import User
    test_user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"]),
        is_active=True
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    db.close()
    
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    """创建测试客户端"""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def token(client):
    """获取认证令牌"""
    response = client.post(
        "/api/user/login",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    return token_data["access_token"]

# 测试健康检查接口
def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data

# 测试用户注册接口
def test_user_register(client):
    response = client.post(
        "/api/user/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert "id" in data

# 测试用户登录接口
def test_user_login(client):
    response = client.post(
        "/api/user/login",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

# 测试获取当前用户信息接口
def test_get_user_me(client, token):
    response = client.get(
        "/api/user/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert "id" in data

# 测试创建角色接口
def test_create_character(client, token):
    response = client.post(
        "/api/character/create",
        headers={"Authorization": f"Bearer {token}"},
        json=test_character_data
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_character_data["name"]
    assert data["birth_time"] == test_character_data["birth_time"]
    assert "id" in data
    assert "fate_score" in data
    assert "attributes" in data
    assert "personality" in data
    
    # 保存角色ID用于后续测试
    test_character_data["id"] = data["id"]

# 测试获取角色列表接口
def test_get_characters(client, token):
    # 首先确保创建了一个角色
    if "id" not in test_character_data:
        test_create_character(client, token)
    
    response = client.get(
        "/api/character",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == test_character_data["name"]

# 测试获取角色详情接口
def test_get_character_detail(client, token):
    # 首先确保创建了一个角色
    if "id" not in test_character_data:
        test_create_character(client, token)
    
    char_id = test_character_data["id"]
    response = client.get(
        f"/api/character/{char_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == char_id
    assert data["name"] == test_character_data["name"]

# 测试主页接口
def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "description" in data
    assert "version" in data 