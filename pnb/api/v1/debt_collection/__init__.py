from fastapi.routing import APIRouter
from .transcript_summarizer import router as transcript_summarizer_router

router = APIRouter(prefix="/debt_collection")
router.include_router(transcript_summarizer_router)
