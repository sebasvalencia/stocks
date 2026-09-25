from app.funds.models import FundUnitValue
from app.services.variation import variation_points


class _PriceLike:
    def __init__(self, year: int, month: int, price: object) -> None:
        self.year = year
        self.month = month
        self.price = price


def unit_value_variation_points(values: list[FundUnitValue]) -> list[dict]:
    return variation_points([_PriceLike(v.year, v.month, v.value) for v in values])
