from fastapi import APIRouter, HTTPException, Query, Depends, Body

router = APIRouter(prefix="/health-check", tags=["Health Check"])

@router.get("/")
async def health_check():
    result = {'success':1, "message": "OK"}
    if not result:
        raise HTTPException(status_code=404, detail="Health Check failed")
    return result