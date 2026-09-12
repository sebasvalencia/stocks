from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Broker
from app.schemas import BrokerIn, BrokerOut

router = APIRouter(prefix="/brokers", tags=["brokers"])


@router.get("", response_model=list[BrokerOut])
def list_brokers(db: Session = Depends(get_db)) -> list[Broker]:
    return list(db.scalars(select(Broker).order_by(Broker.name)).all())


@router.get("/{broker_id}", response_model=BrokerOut)
def get_one(broker_id: int, db: Session = Depends(get_db)) -> Broker:
    row = db.get(Broker, broker_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "broker_not_found")
    return row


@router.post("", response_model=BrokerOut, status_code=status.HTTP_201_CREATED)
def create(body: BrokerIn, db: Session = Depends(get_db)) -> Broker:
    row = Broker(name=body.name.strip())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "broker_exists")
    db.refresh(row)
    return row


@router.put("/{broker_id}", response_model=BrokerOut)
def update(broker_id: int, body: BrokerIn, db: Session = Depends(get_db)) -> Broker:
    row = db.get(Broker, broker_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "broker_not_found")
    row.name = body.name.strip()
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "broker_exists")
    db.refresh(row)
    return row


@router.delete("/{broker_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(broker_id: int, db: Session = Depends(get_db)) -> None:
    row = db.get(Broker, broker_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "broker_not_found")
    db.delete(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "cannot_delete_broker")
