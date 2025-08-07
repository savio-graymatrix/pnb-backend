from fastapi.routing import APIRouter
from .credit_assist import router as credit_assist_router
from .health_check import router as health_check_router
from .procurement import router as procurement_router
from .sales import router as sales_router
from .soc import router as soc_router
from .file_upload import router as file_upload_router
from .call_center import router as call_center_router
from .jd_generator import router as jd_generator_router

router = APIRouter(prefix="/v1")
router.include_router(credit_assist_router)
router.include_router(procurement_router)
router.include_router(sales_router)
router.include_router(soc_router)
router.include_router(health_check_router)
router.include_router(file_upload_router)
router.include_router(call_center_router)
router.include_router(jd_generator_router)
