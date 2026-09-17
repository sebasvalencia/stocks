--
-- PostgreSQL database dump
--

\restrict GkOBB2OOzBL7RAefkOZIIGj8dthU8AWlNMbjNYHb8eQTsP7OEzexLhn07P143Sn

-- Dumped from database version 16.14
-- Dumped by pg_dump version 16.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.monthly_price DROP CONSTRAINT IF EXISTS precio_mensual_instrumento_id_fkey;
ALTER TABLE IF EXISTS ONLY public.price_target DROP CONSTRAINT IF EXISTS objetivo_precio_instrumento_id_fkey;
ALTER TABLE IF EXISTS ONLY public.trade DROP CONSTRAINT IF EXISTS movimiento_instrumento_id_fkey;
ALTER TABLE IF EXISTS ONLY public.trade DROP CONSTRAINT IF EXISTS movimiento_corredor_id_fkey;
ALTER TABLE IF EXISTS ONLY public.price_target DROP CONSTRAINT IF EXISTS uq_price_target_instrument_period;
ALTER TABLE IF EXISTS ONLY public.monthly_price DROP CONSTRAINT IF EXISTS uq_monthly_price_instrument_period;
ALTER TABLE IF EXISTS ONLY public.fx_rate DROP CONSTRAINT IF EXISTS uq_fx_rate_period;
ALTER TABLE IF EXISTS ONLY public.monthly_price DROP CONSTRAINT IF EXISTS precio_mensual_pkey;
ALTER TABLE IF EXISTS ONLY public.price_target DROP CONSTRAINT IF EXISTS objetivo_precio_pkey;
ALTER TABLE IF EXISTS ONLY public.trade DROP CONSTRAINT IF EXISTS movimiento_pkey;
ALTER TABLE IF EXISTS ONLY public.instrument DROP CONSTRAINT IF EXISTS instrumento_pkey;
ALTER TABLE IF EXISTS ONLY public.instrument DROP CONSTRAINT IF EXISTS instrumento_nombre_key;
ALTER TABLE IF EXISTS ONLY public.fx_rate DROP CONSTRAINT IF EXISTS fx_rate_pkey;
ALTER TABLE IF EXISTS ONLY public.broker DROP CONSTRAINT IF EXISTS corredor_pkey;
ALTER TABLE IF EXISTS ONLY public.broker DROP CONSTRAINT IF EXISTS corredor_nombre_key;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS public.trade ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.price_target ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.monthly_price ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.instrument ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.fx_rate ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.broker ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.precio_mensual_id_seq;
DROP SEQUENCE IF EXISTS public.objetivo_precio_id_seq;
DROP TABLE IF EXISTS public.price_target;
DROP SEQUENCE IF EXISTS public.movimiento_id_seq;
DROP TABLE IF EXISTS public.trade;
DROP TABLE IF EXISTS public.monthly_price;
DROP SEQUENCE IF EXISTS public.instrumento_id_seq;
DROP TABLE IF EXISTS public.instrument;
DROP SEQUENCE IF EXISTS public.fx_rate_id_seq;
DROP TABLE IF EXISTS public.fx_rate;
DROP SEQUENCE IF EXISTS public.corredor_id_seq;
DROP TABLE IF EXISTS public.broker;
DROP TABLE IF EXISTS public.alembic_version;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: broker; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.broker (
    id integer NOT NULL,
    name character varying(120) NOT NULL
);


--
-- Name: corredor_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.corredor_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: corredor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.corredor_id_seq OWNED BY public.broker.id;


--
-- Name: fx_rate; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fx_rate (
    id integer NOT NULL,
    year smallint NOT NULL,
    month smallint NOT NULL,
    cop_per_usd numeric(18,4) NOT NULL,
    CONSTRAINT ck_fx_rate_month CHECK (((month >= 1) AND (month <= 12))),
    CONSTRAINT ck_fx_rate_value CHECK ((cop_per_usd > (0)::numeric))
);


--
-- Name: fx_rate_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.fx_rate_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fx_rate_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.fx_rate_id_seq OWNED BY public.fx_rate.id;


--
-- Name: instrument; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.instrument (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    active boolean DEFAULT true NOT NULL,
    currency character varying(3) DEFAULT 'COP'::character varying NOT NULL,
    CONSTRAINT ck_instrument_currency CHECK (((currency)::text = ANY ((ARRAY['COP'::character varying, 'USD'::character varying])::text[])))
);


--
-- Name: instrumento_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.instrumento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: instrumento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.instrumento_id_seq OWNED BY public.instrument.id;


--
-- Name: monthly_price; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.monthly_price (
    id integer NOT NULL,
    instrument_id integer NOT NULL,
    year smallint NOT NULL,
    month smallint NOT NULL,
    price numeric(18,4) NOT NULL,
    CONSTRAINT ck_monthly_price_month CHECK (((month >= 1) AND (month <= 12))),
    CONSTRAINT ck_monthly_price_value CHECK ((price > (0)::numeric))
);


--
-- Name: trade; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.trade (
    id integer NOT NULL,
    instrument_id integer NOT NULL,
    broker_id integer NOT NULL,
    type character varying(10) NOT NULL,
    year smallint NOT NULL,
    month smallint,
    quantity numeric(18,6) NOT NULL,
    commission numeric(18,2) NOT NULL,
    CONSTRAINT ck_trade_commission CHECK ((commission >= (0)::numeric)),
    CONSTRAINT ck_trade_month CHECK (((month IS NULL) OR ((month >= 1) AND (month <= 12)))),
    CONSTRAINT ck_trade_quantity CHECK ((quantity > (0)::numeric)),
    CONSTRAINT ck_trade_type CHECK (((type)::text = ANY (ARRAY[('buy'::character varying)::text, ('sell'::character varying)::text])))
);


--
-- Name: movimiento_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.movimiento_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: movimiento_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.movimiento_id_seq OWNED BY public.trade.id;


--
-- Name: price_target; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.price_target (
    id integer NOT NULL,
    instrument_id integer NOT NULL,
    year smallint NOT NULL,
    month smallint NOT NULL,
    price numeric(18,4) NOT NULL,
    CONSTRAINT ck_price_target_month CHECK (((month >= 1) AND (month <= 12))),
    CONSTRAINT ck_price_target_value CHECK ((price > (0)::numeric))
);


--
-- Name: objetivo_precio_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.objetivo_precio_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: objetivo_precio_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.objetivo_precio_id_seq OWNED BY public.price_target.id;


--
-- Name: precio_mensual_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.precio_mensual_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: precio_mensual_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.precio_mensual_id_seq OWNED BY public.monthly_price.id;


--
-- Name: broker id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.broker ALTER COLUMN id SET DEFAULT nextval('public.corredor_id_seq'::regclass);


--
-- Name: fx_rate id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fx_rate ALTER COLUMN id SET DEFAULT nextval('public.fx_rate_id_seq'::regclass);


--
-- Name: instrument id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instrument ALTER COLUMN id SET DEFAULT nextval('public.instrumento_id_seq'::regclass);


--
-- Name: monthly_price id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.monthly_price ALTER COLUMN id SET DEFAULT nextval('public.precio_mensual_id_seq'::regclass);


--
-- Name: price_target id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.price_target ALTER COLUMN id SET DEFAULT nextval('public.objetivo_precio_id_seq'::regclass);


--
-- Name: trade id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trade ALTER COLUMN id SET DEFAULT nextval('public.movimiento_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
005_instrument_currency
\.


--
-- Data for Name: broker; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.broker (id, name) FROM stdin;
34	Andes Broker
35	Litoral Valores
\.


--
-- Data for Name: fx_rate; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fx_rate (id, year, month, cop_per_usd) FROM stdin;
10	2026	6	4120.0000
11	2026	7	4085.0000
12	2026	8	4010.0000
\.


--
-- Data for Name: instrument; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.instrument (id, name, active, currency) FROM stdin;
36	Cafe Andino	t	COP
37	Sol Energia	t	COP
38	Rio Banco	t	COP
39	Sierra Metales	t	COP
40	Nube Telecom	t	USD
\.


--
-- Data for Name: monthly_price; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.monthly_price (id, instrument_id, year, month, price) FROM stdin;
508	36	2026	1	12400.0000
509	36	2026	2	12650.0000
510	36	2026	3	12800.0000
511	36	2026	4	12550.0000
512	36	2026	5	13100.0000
513	36	2026	6	13400.0000
514	36	2026	7	13680.0000
515	36	2026	8	13920.0000
516	37	2026	1	4800.0000
517	37	2026	2	4950.0000
518	37	2026	4	5100.0000
519	37	2026	5	5280.0000
520	37	2026	6	5400.0000
521	37	2026	7	5550.0000
522	37	2026	8	5720.0000
523	38	2026	1	8200.0000
524	38	2026	2	8350.0000
525	38	2026	3	8500.0000
526	38	2026	4	8480.0000
527	38	2026	5	8700.0000
528	38	2026	6	8900.0000
529	38	2026	7	9100.0000
530	38	2026	8	9280.0000
531	39	2026	1	21000.0000
532	39	2026	2	21400.0000
533	39	2026	3	21800.0000
534	39	2026	4	21200.0000
535	39	2026	5	22000.0000
536	39	2026	6	22500.0000
537	39	2026	7	22900.0000
538	39	2026	8	23300.0000
539	40	2026	1	31.0000
540	40	2026	2	31.8000
541	40	2026	3	32.5000
542	40	2026	4	32.2000
543	40	2026	5	33.0000
544	40	2026	6	33.8000
545	40	2026	7	34.5000
546	40	2026	8	35.2000
547	40	2026	9	36.0000
\.


--
-- Data for Name: price_target; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.price_target (id, instrument_id, year, month, price) FROM stdin;
7	36	2025	6	15000.0000
8	36	2026	8	16000.0000
9	37	2026	8	7000.0000
\.


--
-- Data for Name: trade; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.trade (id, instrument_id, broker_id, type, year, month, quantity, commission) FROM stdin;
7	36	34	buy	2024	3	800.000000	18500.00
8	36	34	buy	2025	2	400.000000	0.00
9	36	34	sell	2025	10	200.000000	6200.00
10	36	35	buy	2025	6	250.000000	9100.00
11	37	34	buy	2024	8	600.000000	14200.00
12	38	35	buy	2025	1	350.000000	0.00
13	39	34	buy	2025	9	180.000000	5300.00
14	40	35	buy	2025	11	90.000000	4.10
\.


--
-- Name: corredor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.corredor_id_seq', 35, true);


--
-- Name: fx_rate_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.fx_rate_id_seq', 12, true);


--
-- Name: instrumento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.instrumento_id_seq', 40, true);


--
-- Name: movimiento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.movimiento_id_seq', 14, true);


--
-- Name: objetivo_precio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.objetivo_precio_id_seq', 9, true);


--
-- Name: precio_mensual_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.precio_mensual_id_seq', 547, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: broker corredor_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.broker
    ADD CONSTRAINT corredor_nombre_key UNIQUE (name);


--
-- Name: broker corredor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.broker
    ADD CONSTRAINT corredor_pkey PRIMARY KEY (id);


--
-- Name: fx_rate fx_rate_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fx_rate
    ADD CONSTRAINT fx_rate_pkey PRIMARY KEY (id);


--
-- Name: instrument instrumento_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instrument
    ADD CONSTRAINT instrumento_nombre_key UNIQUE (name);


--
-- Name: instrument instrumento_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.instrument
    ADD CONSTRAINT instrumento_pkey PRIMARY KEY (id);


--
-- Name: trade movimiento_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trade
    ADD CONSTRAINT movimiento_pkey PRIMARY KEY (id);


--
-- Name: price_target objetivo_precio_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.price_target
    ADD CONSTRAINT objetivo_precio_pkey PRIMARY KEY (id);


--
-- Name: monthly_price precio_mensual_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.monthly_price
    ADD CONSTRAINT precio_mensual_pkey PRIMARY KEY (id);


--
-- Name: fx_rate uq_fx_rate_period; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fx_rate
    ADD CONSTRAINT uq_fx_rate_period UNIQUE (year, month);


--
-- Name: monthly_price uq_monthly_price_instrument_period; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.monthly_price
    ADD CONSTRAINT uq_monthly_price_instrument_period UNIQUE (instrument_id, year, month);


--
-- Name: price_target uq_price_target_instrument_period; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.price_target
    ADD CONSTRAINT uq_price_target_instrument_period UNIQUE (instrument_id, year, month);


--
-- Name: trade movimiento_corredor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trade
    ADD CONSTRAINT movimiento_corredor_id_fkey FOREIGN KEY (broker_id) REFERENCES public.broker(id);


--
-- Name: trade movimiento_instrumento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trade
    ADD CONSTRAINT movimiento_instrumento_id_fkey FOREIGN KEY (instrument_id) REFERENCES public.instrument(id);


--
-- Name: price_target objetivo_precio_instrumento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.price_target
    ADD CONSTRAINT objetivo_precio_instrumento_id_fkey FOREIGN KEY (instrument_id) REFERENCES public.instrument(id);


--
-- Name: monthly_price precio_mensual_instrumento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.monthly_price
    ADD CONSTRAINT precio_mensual_instrumento_id_fkey FOREIGN KEY (instrument_id) REFERENCES public.instrument(id);


--
-- PostgreSQL database dump complete
--

\unrestrict GkOBB2OOzBL7RAefkOZIIGj8dthU8AWlNMbjNYHb8eQTsP7OEzexLhn07P143Sn

