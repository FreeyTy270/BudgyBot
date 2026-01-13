from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from budgybot import persistent_models as pms
from budgybot.records import get_session

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[pms.TransactionPublic])
async def read_transactions(
    session: Annotated[Session, Depends(get_session)],
    bank_account_id: Annotated[int | None, Query(alias="ba_id")] = None,
    limit: int = 100,
    offset: int = 0,
):

    select_stmt = select(pms.Transaction)
    if bank_account_id is not None:
        select_stmt = select_stmt.where(pms.BankAccount.id == bank_account_id)
    select_stmt = select_stmt.offset(offset).limit(limit)

    return session.exec(select_stmt).all()


@router.get("/{tx_id}", response_model=pms.TransactionPublicWithAccount)
async def read_single_transaction(
    session: Annotated[Session, Depends(get_session)], tx_id: int
):

    tx = session.get(pms.Transaction, tx_id)
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.delete("/{tx_id}", response_model=dict[str, bool])
async def delete_transaction(
    session: Annotated[Session, Depends(get_session)], tx_id: int
):
    with session.begin():
        tx = session.get(pms.Transaction, tx_id)
        if tx is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        session.delete(tx)

    return {"success": True}
