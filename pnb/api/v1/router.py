from .instructions import router as instruction_router
from fastapi.routing import APIRouter

router = APIRouter(prefix="/v1")
router.include_router(instruction_router)