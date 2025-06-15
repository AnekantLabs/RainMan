from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.core.db_session import get_db
from app.models.db_models import User
from app.schemas.pydantic_schemas import UserSchema, UserCreate
from app.api.dependencies.users import get_users, create_user, get_user, delete_user
from app.api.dependencies.auth import get_current_active_user

user_router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@user_router.get('/', response_model=list[UserSchema])
def user_list(db: Session = Depends(get_db)):
    db_users = get_users(db)

    return db_users


@user_router.get('/me', response_model=UserSchema)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return current_user



@user_router.get('/{user_id}', response_model=UserSchema)
def user_detail(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@user_router.delete('/{user_id}')
def user_delete(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    delete_user(db, db_user.id)
    return {"message": "User deleted"}


@user_router.post("/", response_model=UserSchema)
def user_post(user: UserCreate, db:Session = Depends(get_db)):
    return create_user(db, user)