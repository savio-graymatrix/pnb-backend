from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pnb.api import router as api_router
from pnb.db.stores.MongoStore import MONGO_STORE
from pnb.langgraph.workflows import setup_graphs
from pnb import SETTINGS

@asynccontextmanager
async def lifespan(app: FastAPI):
    await MONGO_STORE.connect()
    await setup_graphs()
    yield
    await MONGO_STORE.disconnect()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
        CORSMiddleware,
        allow_origins=SETTINGS.ALLOWED_HOSTS,  
        allow_credentials=True,
        allow_methods=["*"],  
        allow_headers=["*"],
    )
app.include_router(api_router)
