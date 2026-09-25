from fastapi import APIRouter

from app.funds.routers import fiduciaries, funds, summary, targets, trades, unit_values

router = APIRouter(prefix="/funds")
router.include_router(fiduciaries.router)
router.include_router(funds.router)
router.include_router(trades.router)
router.include_router(unit_values.router)
router.include_router(targets.router)
router.include_router(summary.router)
