# Stocks

**English** | [Español](README.es.md)

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Track a stock portfolio in Colombia (COP) and the United States (USD). Buys, sells, per-trade commission, month-by-month market prices, and a sell target per holding are entered by hand. Balance, current value, percentages, and progress to target are calculated; they are not stored twice.

## Features

- **Catalog** of holdings (instruments) and brokers, with unique names. Each holding has a quote currency: **COP** or **USD**.
- **Active / inactive** state per holding. An inactive one does not add to the total or appear in weight %. Prices and trades are kept.
- **Buys and sells** per holding + broker pair (year required, month optional, quantity > 0, **commission in the holding’s currency** ≥ 0).
- **Calculated balance**: `buys − sells` per broker. A partial sell lowers the balance; a full sell leaves it at 0; a sell larger than the balance is rejected. There is no negative balance.
- **Monthly prices** per holding (not per broker), in a year × month grid.
- **Missing-price banner**: if an active holding lacks the current month’s price, Summary and Prices show a banner. On Prices, those cells are marked. The month comes from the browser (not the container’s UTC clock).
- **Sell target price** per holding, one value per month. History is kept; the current target is the most recent date. Same month = update.
- **Summary**: current total = Σ (`balance × last price`) for **active** holdings only. If the price is missing, the position is marked “no price” and stays out of the total.
- **Charts**: portfolio weight % (pie), monthly price % change (line), and **progress to target** (`last market / current target`). A gap month does not invent a change or a progress point.
- **Theme, language, display currency**: compact selects in the header (dark / light, ES / EN / IT, COP / USD). Preference is stored in `localStorage`. Holding and broker names are not translated.
- **Quote currency vs display**: prices, targets, and commission are stored in the holding’s currency. The header COP / USD toggle converts with that month’s TRM (`cop_per_usd`). Same-currency view does not need a rate. If the rate is missing for a cross-currency amount, the UI shows “no FX”; it does not invent one.
- **Initial seed**: 11 holdings (Ecopetrol, Celsia, ETB, GEB, Mineros, PG Argos, PG SURA, Cemagros, PF Cemagros, Grupo Argos, Grupo Sura), all **COP**, and 2 brokers (D Corredores, Trii).



## Demo

![Walkthrough](demo/demo.gif)

### Business rules


| Situation                                              | Behavior                                                            |
| ------------------------------------------------------ | ------------------------------------------------------------------- |
| Same holding at two brokers                            | Two positions, one market price                                     |
| Deactivate with balance > 0 (sum across all brokers)   | 400 error                                                           |
| Buy an inactive holding                                | 400 error; reactivate it first                                      |
| Delete a trade if the balance would go negative        | 400 error                                                           |
| Delete a holding or broker that still has related data | 409 error                                                           |
| Change for a month                                     | Only if that month **and** the previous calendar month have a price |
| Commission                                             | ≥ 0 in the holding’s currency; not part of the total                |
| Change a holding’s quote currency                      | 400 error if it already has trades, prices, or targets              |
| Progress to target                                     | Only if there is a market price **and** a current target            |
| Pending prices for the month                           | Only **active** holdings missing a cell in the current month        |
| Cross-currency view without that month’s FX rate       | No conversion; the UI shows “no FX”                                 |


Persisted currency: **COP or USD per holding**. The header toggle is display only: `amount_usd = amount_cop / cop_per_usd` and `amount_cop = amount_usd × cop_per_usd` with that **month’s** TRM.

## How it works

Typical flow: add holding (COP or USD) and broker → record buys (commission in that currency) → if the banner warns, enter this month’s prices → set a sell target → see total, weight %, change, and progress on Summary. Use the header toggle to view the mixed portfolio in COP or USD.

```mermaid
sequenceDiagram
  actor User
  participant Web as React
  participant API as FastAPI
  participant DB as PostgreSQL

  User->>Web: Buy / sell
  Web->>API: POST /trades
  API->>API: validate_trade
  API->>DB: balance for holding+broker pair
  alt sell > balance or holding inactive
    API-->>Web: 400
  else ok
    API->>DB: INSERT trade
    API-->>Web: 201
  end

  User->>Web: Open Summary
  Web->>API: GET /summary
  API->>DB: trades and monthly_price
  API->>API: balance × last price (active only)
  API-->>Web: total + positions + weight %
```



On start, the `api` container runs the Alembic migration, the catalog seed, and Uvicorn.

## Stack


| Layer       | Technology                                                                      |
| ----------- | ------------------------------------------------------------------------------- |
| UI          | React 19, TypeScript, Vite 6, Tailwind CSS 3, React Router 7, Recharts, i18next |
| API         | Python 3.12, FastAPI, Pydantic v2, uv                                           |
| Persistence | PostgreSQL 16, SQLAlchemy 2, Alembic                                            |
| Tests       | pytest, httpx (`TestClient`)                                                    |
| Packaging   | Docker Compose (`db`, `api`, `web` services)                                    |




## How to run



### With Docker (recommended)

Requirements: Docker Desktop.

Copy environment variables to (`.env`):

```bash
cp .env.example .env   # Windows: copy .env.example .env
docker compose up --build
```

Note: Edit `.env` before the first `up` if you want different secrets. If Postgres was already initialized with the `pgdata` volume, changing `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` does **not** update that instance; you have to delete the volume or restore a dump.


| Service    | URL                                                                                                                         |
| ---------- | --------------------------------------------------------------------------------------------------------------------------- |
| UI         | [http://localhost:5173](http://localhost:5173)                                                                              |
| API        | [http://localhost:8000](http://localhost:8000)                                                                              |
| Health     | [http://localhost:8000/health](http://localhost:8000/health)                                                                |
| OpenAPI    | [http://localhost:8000/docs](http://localhost:8000/docs)                                                                    |
| PostgreSQL | `localhost:${POSTGRES_PORT}` — user / password / DB in `.env`                                                               |
| pgAdmin    | [http://localhost:${PGADMIN_PORT}](http://localhost:${PGADMIN_PORT}) — `PGADMIN_DEFAULT_EMAIL` / `PGADMIN_DEFAULT_PASSWORD` |


To run in the background: `docker compose up --build -d`.

pgAdmin ships in the same Compose file. In the left tree open **Servers → stocks**. The first time it asks for the Postgres password (`POSTGRES_PASSWORD`). Internal host: `db` (not `localhost`). If you change `POSTGRES_USER` or `POSTGRES_DB`, update `pgadmin/servers.json`.

pgAdmin only, without rebuilding the rest:

```bash
docker compose up -d pgadmin
```



### Environment variables


| Variable                                              | Use                                                                                      |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Database user, password, and name                                                        |
| `POSTGRES_PORT`                                       | Postgres port on the host (default 5432)                                                 |
| `DATABASE_URL`                                        | API/Alembic **outside** Compose (`localhost`). Compose mounts another URL with host `db` |
| `VITE_API_URL`                                        | API origin used by the frontend                                                          |
| `PGADMIN_DEFAULT_EMAIL` / `PGADMIN_DEFAULT_PASSWORD`  | pgAdmin login                                                                            |
| `PGADMIN_PORT`                                        | pgAdmin port on the host (default 5050)                                                  |


## Layout

```
acciones/
├── docker-compose.yml
├── .env.example
├── LICENSE
├── README.md
├── README.es.md
├── backups/backup.ps1
├── demo/
│   ├── demo.sql             # fictional portfolio (does go to git)
│   ├── demo.gif             # walkthrough in the README
│   └── demo-thumb.png       # preview if there is a YouTube/Loom video
├── pgadmin/servers.json
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── alembic.ini
│   ├── alembic/versions/        # 001 3NF, 002 commission + target, 003 English, 004 FX, 005 currency
│   ├── app/
│   │   ├── main.py              # FastAPI, CORS, /health
│   │   ├── config.py            # DATABASE_URL (no default; comes from the environment)
│   │   ├── database.py          # engine, session, Base
│   │   ├── models.py            # 3NF ORM (English)
│   │   ├── schemas.py           # Pydantic input/output
│   │   ├── seed.py              # 11 holdings + 2 brokers (only if the catalog is empty)
│   │   ├── seed_demo.py         # fictional README portfolio
│   │   ├── routers/             # brokers, instruments, trades, prices, targets, summary, fx
│   │   └── services/            # rules, balances, variation, target
│   └── tests/
└── frontend/
    ├── Dockerfile
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx              # routes, theme, language, and COP/USD
    │   ├── api.ts               # HTTP client
    │   ├── i18n.ts              # es / en / it
    │   ├── theme.tsx            # dark / light
    │   ├── BannerPrecios.tsx    # missing-price notice for the current month
    │   └── pages/               # Summary, Prices, Trades, Catalog, FxRates
    └── ...
```



## Database diagram

```mermaid
erDiagram
  BROKER {
    int id PK
    varchar name UK
  }
  INSTRUMENT {
    int id PK
    varchar name UK
    boolean active
    varchar currency "COP | USD"
  }
  TRADE {
    int id PK
    int instrument_id FK
    int broker_id FK
    varchar type "buy | sell"
    smallint year
    smallint month "nullable 1-12"
    numeric quantity "> 0"
    numeric commission ">= 0 native"
  }
  MONTHLY_PRICE {
    int id PK
    int instrument_id FK
    smallint year
    smallint month "1-12"
    numeric price "> 0"
  }
  PRICE_TARGET {
    int id PK
    int instrument_id FK
    smallint year
    smallint month "1-12"
    numeric price "> 0"
  }
  FX_RATE {
    int id PK
    smallint year
    smallint month "1-12"
    numeric cop_per_usd "> 0"
  }

  BROKER ||--o{ TRADE : records
  INSTRUMENT ||--o{ TRADE : records
  INSTRUMENT ||--o{ MONTHLY_PRICE : quotes
  INSTRUMENT ||--o{ PRICE_TARGET : targets
```



Constraints:

- `instrument.currency` ∈ `{COP, USD}` (default COP).
- `trade.type` ∈ `{buy, sell}`; `quantity > 0`; `commission >= 0`; `month` null or between 1 and 12.
- `monthly_price` and `price_target` unique per (`instrument_id`, `year`, `month`); `price > 0`.
- `fx_rate` unique per (`year`, `month`); `cop_per_usd > 0`.
- FKs: `trade` → `instrument` and `broker`; `monthly_price` and `price_target` → `instrument`.

Why it is 3NF: every non-key attribute depends only on the PK. The holding name is not copied onto trade, price, or target. Balance, progress, and COP/USD display conversion come from queries.

## Class diagram



### Domain (SQLAlchemy)

```mermaid
classDiagram
  class Broker {
    +int id
    +str name
    +trades: list~Trade~
  }
  class Instrument {
    +int id
    +str name
    +bool active
    +str currency
    +trades: list~Trade~
    +prices: list~MonthlyPrice~
    +targets: list~PriceTarget~
  }
  class Trade {
    +int id
    +int instrument_id
    +int broker_id
    +str type
    +int year
    +int month
    +Decimal quantity
    +Decimal commission
  }
  class MonthlyPrice {
    +int id
    +int instrument_id
    +int year
    +int month
    +Decimal price
  }
  class PriceTarget {
    +int id
    +int instrument_id
    +int year
    +int month
    +Decimal price
  }
  class FxRate {
    +int id
    +int year
    +int month
    +Decimal cop_per_usd
  }

  Broker "1" --> "*" Trade : trades
  Instrument "1" --> "*" Trade : trades
  Instrument "1" --> "*" MonthlyPrice : prices
  Instrument "1" --> "*" PriceTarget : targets
```





## License

MIT. See [LICENSE](LICENSE).

If this project is useful to you, consider starring the repository ⭐ Your support helps the project makes it easier for others to discover.