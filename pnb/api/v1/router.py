from .instructions import router as instruction_router
from .review_set import router as review_set_router
from .chat_stream import router as chat_stream_router
from .review import router as review_router
from fastapi.routing import APIRouter

router = APIRouter(prefix="/v1")
router.include_router(instruction_router)
router.include_router(chat_stream_router)
router.include_router(review_set_router)
router.include_router(review_router)