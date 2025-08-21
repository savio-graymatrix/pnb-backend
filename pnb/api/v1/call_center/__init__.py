from fastapi.routing import APIRouter
from .get_session_token import router as get_session_token_router
from .transcript_suggestion import router as transcript_suggestion_router
from .save_session import router as save_session_router
from .get_session import router as get_session_router
from .get_recordings import router as get_recordings_router
from .call_analysis import router as call_analysis_router

router = APIRouter(prefix="/call_center")
router.include_router(get_session_token_router)
router.include_router(transcript_suggestion_router)
router.include_router(save_session_router)
router.include_router(get_session_router)
router.include_router(get_recordings_router)
router.include_router(call_analysis_router)