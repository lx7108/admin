import asyncio
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.resources import Model
from fastapi_admin.factory import app as admin_factory

from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.character import Character
from app.models.destiny import DestinyNode
from app.models.causal_node import CausalEvent
from app.models.fate_nft import FateNFT
from app.models.social_graph import Relationship
from app.models.society import Regime, SocialClass

DATABASE_URL = "postgresql+asyncpg://admin:admin@db:5432/h_pulse"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key='!secret')

async def on_startup():
    await admin_factory(
        app,
        admin_path="/admin",
        engine=engine,
        session_maker=async_session,
        providers=[
            UsernamePasswordProvider(admin_model=User)
        ],
        resources=[
            Model(User),
            Model(Character),
            Model(DestinyNode),
            Model(CausalEvent),
            Model(FateNFT),
            Model(Relationship),
            Model(Regime),
            Model(SocialClass)
        ]
    )

app.add_event_handler("startup", on_startup)
