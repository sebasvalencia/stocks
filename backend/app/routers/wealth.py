from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.funds.routers.summary import build_fund_summary
from app.routers.summary import build_equity_summary
from app.schemas import WealthOut

router = APIRouter(tags=["wealth"])


@router.get("/wealth", response_model=WealthOut)
def wealth(db: Session = Depends(get_db)) -> WealthOut:
    equities = build_equity_summary(db)
    funds = build_fund_summary(db)
    total = Decimal(equities.total) + Decimal(funds.total)
    return WealthOut(equities=equities, funds=funds, total=total)
