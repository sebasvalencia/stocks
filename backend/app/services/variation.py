from decimal import Decimal

from app.models import MonthlyPrice


def previous_calendar_month(year: int, month: int) -> tuple[int, int]:
    if month == 1:
        return year - 1, 12
    return year, month - 1


def variation_points(prices: list[MonthlyPrice]) -> list[dict]:
    """Variation only if the previous calendar month exists. Gaps are not filled."""
    by_period = {(p.year, p.month): p.price for p in prices}
    points: list[dict] = []
    for p in sorted(prices, key=lambda x: (x.year, x.month)):
        py, pm = previous_calendar_month(p.year, p.month)
        prev = by_period.get((py, pm))
        var = None
        if prev is not None and prev != 0:
            var = (Decimal(p.price) - Decimal(prev)) / Decimal(prev) * Decimal(100)
        points.append(
            {
                "year": p.year,
                "month": p.month,
                "price": Decimal(p.price),
                "variation_pct": var,
            }
        )
    return points
