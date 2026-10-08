from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.user import User
from app.schemas.users import UserCreateRequestSchema, UserUpdateRequestSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/")
async def create_user(
        data: UserCreateRequestSchema,
        session: AsyncSession = Depends(get_async_session)
):
    user = User(
        name=data.name,
        email=data.email,
        hashed_password=data.password,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {"status": "ok", "data": user}


@router.get("/")
async def get_users(
        session: AsyncSession = Depends(get_async_session)
):
    # users = await session.get(User)
    result = await session.execute(
        select(User)
    )
    users = result.scalars().all()
    return {"status": "ok", "data": users}


@router.get("/{user_id}")
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    return {
        "status": "ok",
        "data": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        },
    }


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    data: UserUpdateRequestSchema,
    session: AsyncSession = Depends(get_async_session),
):
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.name = data.name

    await session.commit()
    await session.refresh(user)

    return {
        "status": "ok",
        "data": {
            "id": user.id,
            "name": user.name,
        },
    }


@router.delete("/{user_id}")
async def delete_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    await session.delete(user)
    await session.commit()

    return {"status": "ok"}
