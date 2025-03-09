
from fastapi import APIRouter

# this is a router
router = APIRouter()

@router.get("/")
async def root():
    return {"message": "tryna create a fast api project"}

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}