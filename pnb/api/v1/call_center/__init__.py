from fastapi.routing import APIRouter
from .get_session_token import router as get_session_token_router
from .transcript_suggestion import router as transcript_suggestion_router

router = APIRouter(prefix="/call_center")
router.include_router(get_session_token_router)
router.include_router(transcript_suggestion_router)