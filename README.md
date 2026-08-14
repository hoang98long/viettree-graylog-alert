# ASA Config Monitor

A small FastAPI MVP that polls Graylog for Cisco ASA (`ASA_IP`) logs, detects likely configuration changes, persists deduplicated events in SQLite, optionally alerts Telegram, and exposes a live dashboard.

## Architecture

`ASA → Syslog → Graylog → Graylog REST API → FastAPI → SQLite / Telegram / Dashboard`.

The application never connects directly to the ASA. ASA-to-Graylog syslog forwarding must already exist; this application only needs network access to the Graylog REST API.

## Install and run

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Windows activation: `.venv\Scripts\activate`. Open http://localhost:8000, Swagger at http://localhost:8000/docs, then run `pytest`.

For a safe demo without Graylog, set `MOCK_GRAYLOG=true` and `ENABLE_TELEGRAM=false` in `.env`. The mock emits one ASA configuration event; reload the page after a poll.

## Configuration

All configuration is in `.env` (do not commit it). Set `GRAYLOG_URL`, credentials where required, `ASA_IP`, `GRAYLOG_SEARCH_QUERY`, and Telegram token/chat ID. `GRAYLOG_SEARCH_ENDPOINT` defaults to Graylog's legacy universal relative search endpoint; change it for your Graylog version and adjust `GraylogClient._normalize` if its response differs.

The query narrows logs at Graylog, while `ConfigChangeDetector` makes the independent content decision using editable regex patterns in `app/services/detector.py`. Only messages whose normalized `source` exactly matches `ASA_IP` are processed. On startup a short `INITIAL_LOOKBACK_SECONDS` window is used; later polls overlap slightly and SQLite fingerprints prevent duplicates.

## Telegram

Create a bot through BotFather, start a chat with it, obtain its token and chat ID, set both values in `.env`, then use **Test Telegram** on the dashboard. Failures are saved on the event and never stop polling.

## Docker

```bash
cp .env.example .env
docker compose build
docker compose up -d
```

The container must be able to reach `http://192.168.10.10:9000`; test from its network with `curl http://192.168.10.10:9000/api/system` (or the endpoint appropriate to your Graylog release).

## Demo and troubleshooting

1. ASA emits a configuration syslog event to Graylog.
2. FastAPI polls Graylog, filters the ASA source and detects it.
3. It saves the event, attempts Telegram, and the dashboard refreshes within five seconds.

If Graylog is down, FastAPI remains up and dashboard status becomes `disconnected`; it retries automatically. If Docker cannot reach Graylog, verify routing/firewall rules between the container host and `192.168.10.10:9000`.

## Limits and next steps

This is an MVP: Graylog endpoint/normalization and detector patterns must be tuned using actual ASA logs. It has no authentication, migration framework, retries for failed Telegram delivery, or production-scale queueing. Real log samples are the key input for refining detection rules and source-field normalization.
