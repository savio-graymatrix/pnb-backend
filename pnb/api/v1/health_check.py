from fastapi import APIRouter, HTTPException, Query, Depends, Body

router = APIRouter(prefix="/health_check", tags=["Health Check"])

@router.get("/")
async def health_check():
    result = {'success':1, "message": "OK", "description": "Health Check Approved"}
    if not result:
        raise HTTPException(status_code=404, detail="Health Check failed")
    return result