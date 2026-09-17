from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Broker, Instrument

BROKERS = ["D Corredores", "Trii"]
INSTRUMENTS = [
    "Ecopetrol",
    "Celsia",
    "ETB",
    "GEB",
    "Mineros",
    "PG Argos",
    "PG SURA",
    "Cemagros",
    "PF Cemagros",
    "Grupo Argos",
    "Grupo Sura",
]


def seed(db: Session) -> None:
    if db.scalar(select(func.count()).select_from(Broker)) or db.scalar(
        select(func.count()).select_from(Instrument)
    ):
        return
    existing_b = {n for n in db.scalars(select(Broker.name)).all()}
    for name in BROKERS:
        if name not in existing_b:
            db.add(Broker(name=name))
    existing_i = {n for n in db.scalars(select(Instrument.name)).all()}
    for name in INSTRUMENTS:
        if name not in existing_i:
            db.add(Instrument(name=name, active=True, currency="COP"))
    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
