from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlmodel import Session, select

from budgybot import persistent_models as pms
from budgybot.records import get_session


router = APIRouter(
    prefix="/bankaccount",
    tags=["bankaccount"],
    responses={404: {"description": "Bank Account Not found"}},
)


async def check_ba_exists(
    session: Annotated[Session, Depends(get_session)], ba_id: int
) -> pms.BankAccount:
    ba = session.get(pms.BankAccount, ba_id)
    if ba is None:
        raise HTTPException(status_code=404)
    return ba


@router.get("/", response_model=list[pms.BankAccountPublic])
async def read_all_bank_accounts(
    session: Annotated[Session, Depends(get_session)],
):
    accounts = session.exec(select(pms.BankAccount)).all()
    return accounts


@router.get("/{ba_id}", response_model=pms.BankAccountPublic)
async def read_single_bank_account(
    ba: Annotated[pms.BankAccount, Depends(read_all_bank_accounts)],
):
    return ba


@router.post("/create", response_model=pms.BankAccountPublic, status_code=201)
async def create_bank_account(
    session: Annotated[Session, Depends(get_session)],
    bank_account: pms.BankAccountCreate,
):

    bank = session.get(pms.Bank, bank_account.bank_name)
    if bank is None:
        bank = pms.Bank(name=bank_account.bank_name)
        session.add(bank)

    new_ba = pms.BankAccount.model_validate(bank_account)
    session.add(new_ba)
    session.commit()
    session.refresh(new_ba)
    return new_ba


@router.patch("/{ba_id}", response_model=pms.BankAccountPublic, status_code=200)
async def update_bank_account_info(
    session: Annotated[Session, Depends(get_session)],
    ba_update: pms.BankAccountUpdate,
    ba: pms.BankAccount = Depends(check_ba_exists),
):

    update_data = ba_update.model_dump(exclude_unset=True)
    ba.sqlmodel_update(update_data)
    session.commit()
    session.refresh(ba)
    return ba


@router.delete("/{ba_id}", status_code=200)
async def delete_bank_account(
    session: Annotated[Session, Depends(get_session)], ba_id: int
):

    ba = session.get(pms.BankAccount, ba_id)
    if ba is None:
        raise HTTPException(status_code=404)
    session.delete(ba)
    session.commit()
    return {"success": True}


@router.post(
    "/{ba_id}/update",
    response_model=pms.BankAccountPublicWithTransactions,
    status_code=200,
)
async def update_bank_account_with_statement(
    ba_id: int, file: UploadFile, session: Session = Depends(get_session)
):
    ba = session.get(pms.BankAccount, ba_id)
    if ba is None:
        raise HTTPException(status_code=404)
    ba.consume_csv_record(file)
    session.commit()
    session.refresh(ba)


@router.post(
    "/{ba_id}/sync",
    status_code=200,
    response_model=pms.BankAccountPublicWithTransactions,
)
async def sync_bank_account_with_archives(
    session: Annotated[Session, Depends(get_session)],
    ba: Annotated[pms.BankAccount, Depends(check_ba_exists)],
):

    new_records = ba.find_records()
    if len(new_records) == 0:
        raise HTTPException(
            status_code=404, detail=f"No new records found in {ba.archive_dir}"
        )

    ba.update(session, new_records)
    session.commit()
    session.refresh(ba)
    return ba
