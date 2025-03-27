import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from typing import List
from app.models.character import Character
from app.models.causal_node import CausalEvent
from app.ai_db_utils import save_causal_event, update_character_state

# 模拟决策函数（可替换为 PPO 模型调用）
def simple_decide(character: Character) -> dict:
    # 简化决策逻辑：返回一个假动作
    return {
        "action": "演讲",
        "target_id": None,
        "emotion_impact": {"joy": 0.1},
        "result": {"影响力": 0.05},
        "description": f"{character.name} 发起了一场鼓舞人心的演讲。"
    }

# 多角色自动仿真入口
async def simulate_multiple_agents(session: AsyncSession, limit: int = 10):
    result = await session.execute(select(Character).limit(limit))
    characters: List[Character] = result.scalars().all()

    for character in characters:
        decision = simple_decide(character)

        # 写入因果事件
        event = await save_causal_event(
            session=session,
            actor_id=character.id,
            target_id=decision.get("target_id"),
            action=decision["action"],
            context={"人格": character.personality, "时间": str(datetime.utcnow())},
            result=decision["result"],
            emotion_impact=decision.get("emotion_impact", {}),
            description=decision.get("description", ""),
            impact_score=0.1,
            tags=["自动决策"],
            is_public=True,
            duration=1
        )

        # 更新角色状态
        await update_character_state(
            session=session,
            character_id=character.id,
            last_simulation_date=datetime.utcnow()
        )

        print(f"角色 {character.name} -> 生成事件: {event.action}")
