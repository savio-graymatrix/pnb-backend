from .instructions import router as instruction_router
from .review_set import router as review_set_router
from .chat_stream import router as chat_stream_router
from .review import router as review_router
from .file_upload import router as file_upload_router
from .loan_application import router as loan_application_router
from fastapi.routing import APIRouter

router = APIRouter(prefix="/v1")
router.include_router(instruction_router)
router.include_router(chat_stream_router)
router.include_router(review_set_router)
router.include_router(review_router)
router.include_router(file_upload_router)
router.include_router(loan_application_router)