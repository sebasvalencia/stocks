from decimal import Decimal

from app.models import MonthlyPrice, PriceTarget


def current_target(targets: list[PriceTarget]) -> PriceTarget | None:
    if not targets:
        return None
    return max(targets, key=lambda o: (o.year, o.month, o.id))


def progress_pct(last_price: Decimal | None, target: Decimal | None) -> Decimal | None:
    if last_price is None or target is None or target == 0:
        return None
    return (Decimal(last_price) / Decimal(target)) * Decimal(100)


def last_price(prices: list[MonthlyPrice]) -> MonthlyPrice | None:
    if not prices:
        return None
    return max(prices, key=lambda p: (p.year, p.month))
