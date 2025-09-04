from fastapi.routing import APIRouter
from .chat_stream import router as chat_stream_router
from .lead import router as lead_router

router = APIRouter(prefix="/sales")
router.include_router(chat_stream_router)
router.include_router(lead_router)
