from app.funds.models import FundTarget, FundUnitValue
from app.services.target import progress_pct

__all__ = ["current_target", "last_unit_value", "progress_pct"]


def current_target(targets: list[FundTarget]) -> FundTarget | None:
    if not targets:
        return None
    return max(targets, key=lambda o: (o.year, o.month, o.id))


def last_unit_value(values: list[FundUnitValue]) -> FundUnitValue | None:
    if not values:
        return None
    return max(values, key=lambda p: (p.year, p.month))
