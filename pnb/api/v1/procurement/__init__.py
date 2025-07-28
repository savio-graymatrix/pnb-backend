from fastapi.routing import APIRouter
# from .bids import router as bid_router
from .chat_stream import router as chat_stream_router
from .tender import router as tender_router
from .queries import router as query_router

router = APIRouter(prefix="/procurement")
# router.include_router(bid_router)
router.include_router(chat_stream_router)
router.include_router(tender_router)
router.include_router(query_router)
