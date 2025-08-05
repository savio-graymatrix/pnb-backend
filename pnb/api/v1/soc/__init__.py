
from fastapi.routing import APIRouter
from .soc_chat_stream import router as soc_chat_stream_router
from .soc_file_upload import router as soc_file_upload_router
from .soc_fetch_all_incidents import router as soc_fetch_incidents_router

router = APIRouter(prefix="/soc")
router.include_router(soc_chat_stream_router)
router.include_router(soc_file_upload_router)
router.include_router(soc_fetch_incidents_router)