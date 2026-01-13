from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from budgybot import persistent_models as pms
from budgybot.records import get_session

router = APIRouter(
    prefix="/",
    responses={404: {"description": "Not found"}},
)


@router.get("/")
@router.get("/api")
async def root():
    return {"message": "Welcome to budgybot!!!!"}
