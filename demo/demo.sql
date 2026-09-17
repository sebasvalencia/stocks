-- Fictional portfolio for the README demo video. Not real holdings.
-- Restore (overwrites data, keeps schema):
--   .\backups\backup.ps1 -Restore demo\demo.sql -Force
-- Backup your real DB first: .\backups\backup.ps1

BEGIN;

TRUNCATE TABLE
    public.trade,
    public.monthly_price,
    public.price_target,
    public.fx_rate,
    public.instrument,
    public.broker
RESTART IDENTITY CASCADE;

INSERT INTO public.broker (name) VALUES
    ('Andes Broker'),
    ('Litoral Valores');

INSERT INTO public.instrument (name, active) VALUES
    ('Cafe Andino', TRUE),
    ('Sol Energia', TRUE),
    ('Rio Banco', TRUE),
    ('Sierra Metales', TRUE),
    ('Nube Telecom', TRUE);

INSERT INTO public.trade (instrument_id, broker_id, type, year, month, quantity, commission)
SELECT i.id, b.id, 'buy', 2024, 3, 800, 18500
FROM public.instrument i, public.broker b
WHERE i.name = 'Cafe Andino' AND b.name = 'Andes Broker';

INSERT INTO public.trade (instrument_id, broker_id, type, year, month, quantity, commission)
SELECT i.id, b.id, 'buy', 2025, 2, 400, 0
FROM public.instrument i, public.broker b
WHERE i.name = 'Cafe Andino' AND b.name = 'Andes Broker';

INSERT INTO public.trade (instrument_id, broker_id, type, year, month, quantity, commission)
SELECT i.id, b.id, 'sell', 2025, 10, 200, 6200
FROM public.instrument i, public.broker b
WHERE i.name = 'Cafe Andino' AND b.name = 'Andes Broker';

INSERT INTO public.trade (instrument_id, broker_id, type, year, month, quantity, commission)
SELECT i.id, b.id, 'buy', 2025, 6, 250, 9100
FROM public.instrument i, public.broker b
WHERE i.name = 'Cafe Andino' AND b.name = 'Litoral Valores';

INSERT INTO public.trade (instrument_id, broker_id, type, year, month, quantity, commission)
SELECT i.id, b.id, 'buy', 2024, 8, 600, 14200
FROM public.instrument i, public.broker b
WHERE i.name = 'Sol Energia' AND b.name = 'Andes Broker';

INSERT INTO public.trade (instrument_id, broker_id, type, year, month, quantity, commission)
SELECT i.id, b.id, 'buy', 2025, 1, 350, 0
FROM public.instrument i, public.broker b
WHERE i.name = 'Rio Banco' AND b.name = 'Litoral Valores';

INSERT INTO public.trade (instrument_id, broker_id, type, year, month, quantity, commission)
SELECT i.id, b.id, 'buy', 2025, 9, 180, 5300
FROM public.instrument i, public.broker b
WHERE i.name = 'Sierra Metales' AND b.name = 'Andes Broker';

INSERT INTO public.trade (instrument_id, broker_id, type, year, month, quantity, commission)
SELECT i.id, b.id, 'buy', 2025, 11, 90, 4100
FROM public.instrument i, public.broker b
WHERE i.name = 'Nube Telecom' AND b.name = 'Litoral Valores';

INSERT INTO public.monthly_price (instrument_id, year, month, price)
SELECT i.id, 2026, m.month, m.price
FROM public.instrument i
JOIN (
    VALUES
        (1, 12400.0), (2, 12650.0), (3, 12800.0), (4, 12550.0),
        (5, 13100.0), (6, 13400.0), (7, 13680.0), (8, 13920.0)
) AS m(month, price) ON TRUE
WHERE i.name = 'Cafe Andino';

INSERT INTO public.monthly_price (instrument_id, year, month, price)
SELECT i.id, 2026, m.month, m.price
FROM public.instrument i
JOIN (
    VALUES
        (1, 4800.0), (2, 4950.0), (4, 5100.0), (5, 5280.0),
        (6, 5400.0), (7, 5550.0), (8, 5720.0)
) AS m(month, price) ON TRUE
WHERE i.name = 'Sol Energia';

INSERT INTO public.monthly_price (instrument_id, year, month, price)
SELECT i.id, 2026, m.month, m.price
FROM public.instrument i
JOIN (
    VALUES
        (1, 8200.0), (2, 8350.0), (3, 8500.0), (4, 8480.0),
        (5, 8700.0), (6, 8900.0), (7, 9100.0), (8, 9280.0)
) AS m(month, price) ON TRUE
WHERE i.name = 'Rio Banco';

INSERT INTO public.monthly_price (instrument_id, year, month, price)
SELECT i.id, 2026, m.month, m.price
FROM public.instrument i
JOIN (
    VALUES
        (1, 21000.0), (2, 21400.0), (3, 21800.0), (4, 21200.0),
        (5, 22000.0), (6, 22500.0), (7, 22900.0), (8, 23300.0)
) AS m(month, price) ON TRUE
WHERE i.name = 'Sierra Metales';

INSERT INTO public.monthly_price (instrument_id, year, month, price)
SELECT i.id, 2026, m.month, m.price
FROM public.instrument i
JOIN (
    VALUES
        (1, 3100.0), (2, 3180.0), (3, 3250.0), (4, 3220.0),
        (5, 3300.0), (6, 3380.0), (7, 3450.0), (8, 3520.0), (9, 3600.0)
) AS m(month, price) ON TRUE
WHERE i.name = 'Nube Telecom';

INSERT INTO public.price_target (instrument_id, year, month, price)
SELECT i.id, 2025, 6, 15000 FROM public.instrument i WHERE i.name = 'Cafe Andino';
INSERT INTO public.price_target (instrument_id, year, month, price)
SELECT i.id, 2026, 8, 16000 FROM public.instrument i WHERE i.name = 'Cafe Andino';
INSERT INTO public.price_target (instrument_id, year, month, price)
SELECT i.id, 2026, 8, 7000 FROM public.instrument i WHERE i.name = 'Sol Energia';

INSERT INTO public.fx_rate (year, month, cop_per_usd) VALUES
    (2026, 6, 4120),
    (2026, 7, 4085),
    (2026, 8, 4010);

COMMIT;
