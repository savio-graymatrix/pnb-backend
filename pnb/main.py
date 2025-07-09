from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pnb.api.router import router as api_router
from pnb.db.stores.MongoStore import MONGO_STORE
from pnb.langgraph.workflows import setup_graphs

@asynccontextmanager
async def lifespan(app: FastAPI):
    await MONGO_STORE.connect()
    await setup_graphs()
    yield
    await MONGO_STORE.disconnect()

app = FastAPI(lifespan=lifespan)
app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "https://798ef4034ebe.ngrok-free.app", "http://localhost:8000"],  
        allow_credentials=True,
        allow_methods=["*"],  
        allow_headers=["*"],
    )
app.include_router(api_router)
