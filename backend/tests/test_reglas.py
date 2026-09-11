from decimal import Decimal

from fastapi.testclient import TestClient

from app.services.variacion import puntos_variacion


def _ids(client: TestClient) -> tuple[int, int, int]:
    inst = {r["nombre"]: r["id"] for r in client.get("/instrumentos").json()}
    corr = {r["nombre"]: r["id"] for r in client.get("/corredores").json()}
    return inst["Ecopetrol"], corr["D Corredores"], corr["Trii"]


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_seed_catalogo(client: TestClient) -> None:
    inst = client.get("/instrumentos").json()
    corr = client.get("/corredores").json()
    assert len(inst) == 11
    assert {c["nombre"] for c in corr} == {"D Corredores", "Trii"}
    assert "IBITCO" not in {i["nombre"] for i in inst}


def test_venta_parcial_total_y_exceso(client: TestClient) -> None:
    eco, dcor, _ = _ids(client)
    r = client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "compra",
            "anio": 2007,
            "cantidad": 1500,
        },
    )
    assert r.status_code == 201
    r = client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "venta",
            "anio": 2025,
            "mes": 3,
            "cantidad": 500,
        },
    )
    assert r.status_code == 201
    saldos = client.get("/saldos").json()
    eco_d = next(s for s in saldos if s["corredor_nombre"] == "D Corredores")
    assert Decimal(str(eco_d["saldo"])) == Decimal("1000")

    r = client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "venta",
            "anio": 2025,
            "cantidad": 1000,
        },
    )
    assert r.status_code == 201
    saldos = client.get("/saldos").json()
    eco_d = next(s for s in saldos if s["corredor_nombre"] == "D Corredores")
    assert Decimal(str(eco_d["saldo"])) == Decimal("0")

    r = client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "venta",
            "anio": 2025,
            "cantidad": 1,
        },
    )
    assert r.status_code == 400


def test_venta_no_toca_otro_corredor(client: TestClient) -> None:
    eco, dcor, trii = _ids(client)
    client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "compra",
            "anio": 2007,
            "cantidad": 1500,
        },
    )
    client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": trii,
            "tipo": "compra",
            "anio": 2025,
            "cantidad": 447,
        },
    )
    client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": trii,
            "tipo": "venta",
            "anio": 2025,
            "cantidad": 447,
        },
    )
    saldos = {s["corredor_nombre"]: s["saldo"] for s in client.get("/saldos").json()}
    assert Decimal(str(saldos["D Corredores"])) == Decimal("1500")
    assert Decimal(str(saldos["Trii"])) == Decimal("0")


def test_inactivar_solo_saldo_cero(client: TestClient) -> None:
    eco, dcor, _ = _ids(client)
    client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "compra",
            "anio": 2007,
            "cantidad": 1500,
        },
    )
    r = client.put(f"/instrumentos/{eco}", json={"activo": False})
    assert r.status_code == 400
    client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "venta",
            "anio": 2025,
            "cantidad": 1500,
        },
    )
    r = client.put(f"/instrumentos/{eco}", json={"activo": False})
    assert r.status_code == 200
    assert r.json()["activo"] is False
    r = client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "compra",
            "anio": 2026,
            "cantidad": 10,
        },
    )
    assert r.status_code == 400
    r = client.put(f"/instrumentos/{eco}", json={"activo": True})
    assert r.status_code == 200
    r = client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "compra",
            "anio": 2026,
            "cantidad": 10,
        },
    )
    assert r.status_code == 201


def test_resumen_cantidad_por_precio_y_inactivo_fuera(client: TestClient) -> None:
    eco, dcor, trii = _ids(client)
    client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "compra",
            "anio": 2007,
            "cantidad": 1500,
        },
    )
    client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": trii,
            "tipo": "compra",
            "anio": 2025,
            "cantidad": 447,
        },
    )
    r = client.put(
        "/precios",
        json={"instrumento_id": eco, "anio": 2026, "mes": 9, "precio": 2645},
    )
    assert r.status_code == 200
    res = client.get("/resumen").json()
    assert Decimal(str(res["total"])) == Decimal("1500") * Decimal("2645") + Decimal("447") * Decimal(
        "2645"
    )
    assert len(res["posiciones"]) == 2
    client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": trii,
            "tipo": "venta",
            "anio": 2026,
            "cantidad": 447,
        },
    )
    client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "venta",
            "anio": 2026,
            "cantidad": 1500,
        },
    )
    client.put(f"/instrumentos/{eco}", json={"activo": False})
    res = client.get("/resumen").json()
    assert Decimal(str(res["total"])) == Decimal("0")
    assert res["posiciones"] == []


def test_sin_precio_no_suma(client: TestClient) -> None:
    eco, dcor, _ = _ids(client)
    client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "compra",
            "anio": 2007,
            "cantidad": 10,
        },
    )
    res = client.get("/resumen").json()
    assert Decimal(str(res["total"])) == Decimal("0")
    assert res["posiciones"][0]["sin_precio"] is True


def test_variacion_mes_hueco_no_inventa() -> None:
    class P:
        def __init__(self, anio: int, mes: int, precio: str) -> None:
            self.anio = anio
            self.mes = mes
            self.precio = Decimal(precio)

    puntos = puntos_variacion([P(2026, 1, "100"), P(2026, 3, "110")])
    ene = next(p for p in puntos if p["mes"] == 1)
    mar = next(p for p in puntos if p["mes"] == 3)
    assert ene["variacion_pct"] is None
    assert mar["variacion_pct"] is None
    puntos2 = puntos_variacion([P(2026, 1, "100"), P(2026, 2, "110")])
    feb = next(p for p in puntos2 if p["mes"] == 2)
    assert feb["variacion_pct"] == Decimal("10")


def test_comision_se_guarda_y_no_cambia_total(client: TestClient) -> None:
    eco, dcor, _ = _ids(client)
    r = client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "compra",
            "anio": 2007,
            "cantidad": 10,
            "comision": 12500,
        },
    )
    assert r.status_code == 201
    assert Decimal(str(r.json()["comision"])) == Decimal("12500")
    r = client.put(
        "/precios",
        json={"instrumento_id": eco, "anio": 2026, "mes": 9, "precio": 100},
    )
    assert r.status_code == 200
    res = client.get("/resumen").json()
    assert Decimal(str(res["total"])) == Decimal("1000")


def test_comision_negativa_rechazada(client: TestClient) -> None:
    eco, dcor, _ = _ids(client)
    r = client.post(
        "/movimientos",
        json={
            "instrumento_id": eco,
            "corredor_id": dcor,
            "tipo": "compra",
            "anio": 2007,
            "cantidad": 10,
            "comision": -1,
        },
    )
    assert r.status_code == 422


def test_objetivo_historial_y_avance(client: TestClient) -> None:
    eco, _, _ = _ids(client)
    r = client.put(
        "/objetivos",
        json={"instrumento_id": eco, "anio": 2025, "mes": 1, "precio": 2000},
    )
    assert r.status_code == 200
    r = client.put(
        "/objetivos",
        json={"instrumento_id": eco, "anio": 2026, "mes": 9, "precio": 3000},
    )
    assert r.status_code == 200
    r = client.put(
        "/objetivos",
        json={"instrumento_id": eco, "anio": 2026, "mes": 9, "precio": 3100},
    )
    assert r.status_code == 200
    hist = client.get(f"/objetivos?instrumento_id={eco}").json()
    assert len(hist) == 2
    assert Decimal(str(hist[0]["precio"])) == Decimal("3100")

    client.put("/precios", json={"instrumento_id": eco, "anio": 2026, "mes": 9, "precio": 2480})
    av = client.get(f"/avance-objetivo?instrumento_id={eco}").json()
    assert Decimal(str(av["objetivo"])) == Decimal("3100")
    assert Decimal(str(av["precio_ultimo"])) == Decimal("2480")
    assert Decimal(str(av["avance_pct"])) == (Decimal("2480") / Decimal("3100")) * Decimal("100")


def test_avance_sin_objetivo_ni_precio(client: TestClient) -> None:
    eco, _, _ = _ids(client)
    av = client.get(f"/avance-objetivo?instrumento_id={eco}").json()
    assert av["objetivo"] is None
    assert av["precio_ultimo"] is None
    assert av["avance_pct"] is None


def test_precios_pendientes_solo_activos_sin_precio(client: TestClient) -> None:
    inst = {r["nombre"]: r for r in client.get("/instrumentos").json()}
    eco = inst["Ecopetrol"]["id"]
    celsia = inst["Celsia"]["id"]
    r = client.get("/precios/pendientes", params={"anio": 2026, "mes": 9})
    assert r.status_code == 200
    body = r.json()
    assert body["total_activos"] == 11
    assert body["pendientes"] == 11
    client.put("/precios", json={"instrumento_id": eco, "anio": 2026, "mes": 9, "precio": 2645})
    client.put(f"/instrumentos/{celsia}", json={"activo": False})
    body = client.get("/precios/pendientes", params={"anio": 2026, "mes": 9}).json()
    nombres = {f["instrumento_nombre"] for f in body["faltantes"]}
    assert "Ecopetrol" not in nombres
    assert "Celsia" not in nombres
    assert body["total_activos"] == 10
    assert body["pendientes"] == 9
