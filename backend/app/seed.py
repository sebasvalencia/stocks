from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Corredor, Instrumento

CORREDORES = ["D Corredores", "Trii"]
INSTRUMENTOS = [
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
    existentes_c = {n for n in db.scalars(select(Corredor.nombre)).all()}
    for nombre in CORREDORES:
        if nombre not in existentes_c:
            db.add(Corredor(nombre=nombre))
    existentes_i = {n for n in db.scalars(select(Instrumento.nombre)).all()}
    for nombre in INSTRUMENTOS:
        if nombre not in existentes_i:
            db.add(Instrumento(nombre=nombre, activo=True))
    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
