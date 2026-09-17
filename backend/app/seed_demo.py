from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Broker, FxRate, Instrument, MonthlyPrice, PriceTarget, Trade

DEMO_BROKERS = ["Andes Broker", "Litoral Valores"]
DEMO_INSTRUMENTS = [
    "Cafe Andino",
    "Sol Energia",
    "Rio Banco",
    "Sierra Metales",
    "Nube Telecom",
]


def _dec(value: str | int | float) -> Decimal:
    return Decimal(str(value))


def reset_demo(db: Session) -> None:
    db.execute(delete(Trade))
    db.execute(delete(MonthlyPrice))
    db.execute(delete(PriceTarget))
    db.execute(delete(FxRate))
    db.execute(delete(Instrument))
    db.execute(delete(Broker))
    db.commit()


def seed_demo(db: Session) -> None:
    """Replace catalog and movements with a small fictional portfolio for the README video."""
    reset_demo(db)
    brokers = {name: Broker(name=name) for name in DEMO_BROKERS}
    instruments = {name: Instrument(name=name, active=True) for name in DEMO_INSTRUMENTS}
    db.add_all([*brokers.values(), *instruments.values()])
    db.flush()

    andes = brokers["Andes Broker"]
    litoral = brokers["Litoral Valores"]
    cafe = instruments["Cafe Andino"]
    sol = instruments["Sol Energia"]
    rio = instruments["Rio Banco"]
    sierra = instruments["Sierra Metales"]
    nube = instruments["Nube Telecom"]

    db.add_all(
        [
            Trade(
                instrument_id=cafe.id,
                broker_id=andes.id,
                type="buy",
                year=2024,
                month=3,
                quantity=_dec(800),
                commission=_dec(18500),
            ),
            Trade(
                instrument_id=cafe.id,
                broker_id=andes.id,
                type="buy",
                year=2025,
                month=2,
                quantity=_dec(400),
                commission=_dec(0),
            ),
            Trade(
                instrument_id=cafe.id,
                broker_id=andes.id,
                type="sell",
                year=2025,
                month=10,
                quantity=_dec(200),
                commission=_dec(6200),
            ),
            Trade(
                instrument_id=cafe.id,
                broker_id=litoral.id,
                type="buy",
                year=2025,
                month=6,
                quantity=_dec(250),
                commission=_dec(9100),
            ),
            Trade(
                instrument_id=sol.id,
                broker_id=andes.id,
                type="buy",
                year=2024,
                month=8,
                quantity=_dec(600),
                commission=_dec(14200),
            ),
            Trade(
                instrument_id=rio.id,
                broker_id=litoral.id,
                type="buy",
                year=2025,
                month=1,
                quantity=_dec(350),
                commission=_dec(0),
            ),
            Trade(
                instrument_id=sierra.id,
                broker_id=andes.id,
                type="buy",
                year=2025,
                month=9,
                quantity=_dec(180),
                commission=_dec(5300),
            ),
            Trade(
                instrument_id=nube.id,
                broker_id=litoral.id,
                type="buy",
                year=2025,
                month=11,
                quantity=_dec(90),
                commission=_dec(4100),
            ),
        ]
    )

    cafe_prices = {
        1: "12400",
        2: "12650",
        3: "12800",
        4: "12550",
        5: "13100",
        6: "13400",
        7: "13680",
        8: "13920",
    }
    sol_prices = {
        1: "4800",
        2: "4950",
        4: "5100",
        5: "5280",
        6: "5400",
        7: "5550",
        8: "5720",
    }
    rio_prices = {
        1: "8200",
        2: "8350",
        3: "8500",
        4: "8480",
        5: "8700",
        6: "8900",
        7: "9100",
        8: "9280",
    }
    sierra_prices = {
        1: "21000",
        2: "21400",
        3: "21800",
        4: "21200",
        5: "22000",
        6: "22500",
        7: "22900",
        8: "23300",
    }
    nube_prices = {
        1: "3100",
        2: "3180",
        3: "3250",
        4: "3220",
        5: "3300",
        6: "3380",
        7: "3450",
        8: "3520",
        9: "3600",
    }
    for month, price in cafe_prices.items():
        db.add(MonthlyPrice(instrument_id=cafe.id, year=2026, month=month, price=_dec(price)))
    for month, price in sol_prices.items():
        db.add(MonthlyPrice(instrument_id=sol.id, year=2026, month=month, price=_dec(price)))
    for month, price in rio_prices.items():
        db.add(MonthlyPrice(instrument_id=rio.id, year=2026, month=month, price=_dec(price)))
    for month, price in sierra_prices.items():
        db.add(MonthlyPrice(instrument_id=sierra.id, year=2026, month=month, price=_dec(price)))
    for month, price in nube_prices.items():
        db.add(MonthlyPrice(instrument_id=nube.id, year=2026, month=month, price=_dec(price)))

    db.add_all(
        [
            PriceTarget(instrument_id=cafe.id, year=2025, month=6, price=_dec(15000)),
            PriceTarget(instrument_id=cafe.id, year=2026, month=8, price=_dec(16000)),
            PriceTarget(instrument_id=sol.id, year=2026, month=8, price=_dec(7000)),
            FxRate(year=2026, month=6, cop_per_usd=_dec(4120)),
            FxRate(year=2026, month=7, cop_per_usd=_dec(4085)),
            FxRate(year=2026, month=8, cop_per_usd=_dec(4010)),
        ]
    )
    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        seed_demo(db)
        names = list(db.scalars(select(Instrument.name)).all())
        print("Demo catalog:", ", ".join(names))
    finally:
        db.close()


if __name__ == "__main__":
    main()
