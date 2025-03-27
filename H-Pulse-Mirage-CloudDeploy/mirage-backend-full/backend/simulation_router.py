from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db_session
from app.simulation.multi_agent_simulation import run_multi_agent_simulation

router = APIRouter(prefix="/simulate", tags=["Simulation"])

@router.post("/step")
async def simulate_step(db: AsyncSession = Depends(get_db_session)):
    await run_multi_agent_simulation(session=db, max_steps=1)
    return {"message": "执行 1 步仿真完成"}

@router.post("/batch")
async def simulate_batch(steps: int = 10, db: AsyncSession = Depends(get_db_session)):
    await run_multi_agent_simulation(session=db, max_steps=steps)
    return {"message": f"执行 {steps} 步仿真完成"}
