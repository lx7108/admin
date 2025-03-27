from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database import get_db_session
from app.models.character import Character
from app.models.causal_node import CausalEvent

router = APIRouter(prefix="/stats", tags=["Simulation Stats"])

@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db_session)):
    char_count = await db.scalar(select(func.count()).select_from(Character))
    event_count = await db.scalar(select(func.count()).select_from(CausalEvent))

    recent_active = await db.execute(
        select(Character.name, Character.last_simulation_date)
        .where(Character.last_simulation_date != None)
        .order_by(Character.last_simulation_date.desc())
        .limit(5)
    )
    active_list = [
        {"name": r[0], "last_simulation_date": r[1]} for r in recent_active.all()
    ]

    return {
        "total_characters": char_count,
        "total_events": event_count,
        "recent_active_characters": active_list
    }

@router.get("/timeline")
async def get_event_timeline(days: int = 7, db: AsyncSession = Depends(get_db_session)):
    timeline = []
    today = datetime.utcnow().date()
    for i in range(days):
        day = today - timedelta(days=i)
        count = await db.scalar(
            select(func.count()).select_from(CausalEvent)
            .where(func.date(CausalEvent.timestamp) == day)
        )
        timeline.append({
            "date": day.isoformat(),
            "event_count": count
        })
    return list(reversed(timeline))
