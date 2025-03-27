from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class UserRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str

@app.post("/api/login", response_model=TokenResponse)
@app.post("/api/register", response_model=TokenResponse)
def login(user: UserRequest):
    if user.username and user.password:
        return {"token": "mock-token-123"}
    raise HTTPException(status_code=401, detail="认证失败")

@app.get("/api/characters")
def get_characters():
    return [
        {"id": 1, "name": "刘鑫", "destiny": "平稳"},
        {"id": 2, "name": "沈澄澄", "destiny": "起伏"},
    ]

@app.get("/api/character/{id}")
def get_character(id: int):
    return {
        "id": id,
        "name": "刘鑫",
        "gender": "男",
        "age": 28,
        "occupation": "策略师",
        "destiny": "平稳",
        "bazi": ["丁丑", "丁未", "己未", "庚午"],
        "attributes": {
            "健康": 72,
            "财富": 85,
            "社交": 60,
            "智力": 90,
            "情感": 50
        },
        "fateTrend": [
            {"date": "2025-03-01", "score": 62},
            {"date": "2025-03-05", "score": 70},
            {"date": "2025-03-10", "score": 75},
            {"date": "2025-03-15", "score": 65}
        ],
        "logs": [
            "[2025-03-01] 与角色A建立关系",
            "[2025-03-15] 触发事件：命运转折"
        ]
    }

@app.get("/api/character/{id}/ai-log")
def get_ai_log(id: int):
    return {
        "nodes": [
            {"name": "状态1", "value": 1},
            {"name": "行为A", "value": 1},
            {"name": "状态2", "value": 1},
            {"name": "奖励: +3.2", "value": 1}
        ],
        "links": [
            {"source": "状态1", "target": "行为A"},
            {"source": "行为A", "target": "状态2"},
            {"source": "行为A", "target": "奖励: +3.2"}
        ]
    }

@app.post("/api/simulation/start")
def start_sim():
    return {"status": "运行中"}

@app.post("/api/simulation/stop")
def stop_sim():
    return {"status": "已暂停"}

@app.get("/api/simulation/status")
def sim_status():
    return {"status": "运行中"}
