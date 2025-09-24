from fastapi import APIRouter, Depends

router = APIRouter(prefix="/utils", tags=["utils"])

@router.get("/health")
def health_check() -> bool:
    return True