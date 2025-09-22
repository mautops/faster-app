from contextlib import asynccontextmanager
from fastapi import FastAPI
from tortoise import Tortoise
from faster_app.settings import configs


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(config=configs.TORTOISE_ORM)
    yield
    await Tortoise.close_connections()
