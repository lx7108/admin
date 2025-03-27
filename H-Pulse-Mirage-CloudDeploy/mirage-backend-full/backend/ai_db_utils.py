from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.character import Character
from app.models.causal_node import CausalEvent
from datetime import datetime

async def save_causal_event(session: AsyncSession, actor_id: int, target_id: int, action: str,
                            context: dict, result: dict, emotion_impact: dict = None,
                            social_impact: dict = None, tags: list = None, location: str = None,
                            origin_event_id: int = None, impact_score: float = 0.0,
                            is_public: bool = True, duration: int = 0, description: str = "") -> CausalEvent:
    event = CausalEvent(
        actor_id=actor_id,
        target_id=target_id,
        action=action,
        context=context,
        result=result,
        emotion_impact=emotion_impact or {},
        social_impact=social_impact or {},
        tags=tags or [],
        location=location,
        origin_event=origin_event_id,
        impact_score=impact_score,
        is_public=is_public,
        duration=duration,
        description=description,
        timestamp=datetime.utcnow()
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event

async def update_character_state(session: AsyncSession, character_id: int, new_attributes: dict = None,
                                 new_personality: dict = None, last_simulation_date: datetime = None):
    result = await session.execute(select(Character).where(Character.id == character_id))
    character = result.scalar_one_or_none()
    if not character:
        raise ValueError(f"角色 {character_id} 不存在")

    if new_attributes:
        character.attributes = {**character.attributes, **new_attributes} if character.attributes else new_attributes
    if new_personality:
        character.personality = {**character.personality, **new_personality} if character.personality else new_personality
    if last_simulation_date:
        character.last_simulation_date = last_simulation_date

    await session.commit()
    await session.refresh(character)
    return character
