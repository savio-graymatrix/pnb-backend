
from fastapi.routing import APIRouter
from .jd_chat_stream import router as jd_chat_stream_router

router = APIRouter(prefix="/jd_generator")
router.include_router(jd_chat_stream_router)