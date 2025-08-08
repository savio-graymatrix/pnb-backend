from fastapi.routing import APIRouter
from .chat_stream import router as chat_stream_router

router = APIRouter(prefix="/sales")
router.include_router(chat_stream_router)