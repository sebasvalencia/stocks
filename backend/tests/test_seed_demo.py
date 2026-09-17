from fastapi.testclient import TestClient

from app.seed_demo import DEMO_BROKERS, DEMO_INSTRUMENTS, seed_demo


def test_seed_skips_when_catalog_exists(client: TestClient) -> None:
    names = {r["name"] for r in client.get("/instruments").json()}
    assert "Ecopetrol" in names
    assert "Cafe Andino" not in names


def test_seed_demo_replaces_catalog_with_fiction(db, client: TestClient) -> None:
    seed_demo(db)
    names = {r["name"] for r in client.get("/instruments").json()}
    brokers = {r["name"] for r in client.get("/brokers").json()}
    assert names == set(DEMO_INSTRUMENTS)
    by_name = {r["name"]: r["currency"] for r in client.get("/instruments").json()}
    assert by_name["Nube Telecom"] == "USD"
    assert by_name["Cafe Andino"] == "COP"
    assert brokers == set(DEMO_BROKERS)
    assert "Ecopetrol" not in names
    assert "D Corredores" not in brokers

    trades = client.get("/trades").json()
    assert any(t["type"] == "sell" and t["instrument_name"] == "Cafe Andino" for t in trades)
    assert any(float(t["commission"]) > 0 for t in trades)

    pending = client.get("/prices/pending", params={"year": 2026, "month": 9}).json()
    missing = {row["instrument_name"] for row in pending["missing"]}
    assert "Cafe Andino" in missing
    assert "Nube Telecom" not in missing

    fx_months = {r["month"] for r in client.get("/fx-rates", params={"year": 2026}).json()}
    assert fx_months == {6, 7, 8}

    sol = next(i for i in client.get("/instruments").json() if i["name"] == "Sol Energia")
    points = client.get("/price-variation", params={"instrument_id": sol["id"]}).json()["points"]
    mar = next(p for p in points if p["month"] == 4)
    assert mar["variation_pct"] is None
