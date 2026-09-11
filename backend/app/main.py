from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import corredores, instrumentos, movimientos, objetivos, precios, resumen

app = FastAPI(title="Acciones", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(corredores.router)
app.include_router(instrumentos.router)
app.include_router(movimientos.router)
app.include_router(precios.router)
app.include_router(objetivos.router)
app.include_router(resumen.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
