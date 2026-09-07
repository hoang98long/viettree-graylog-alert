# Implementation Status

## Completed

- Graylog REST API polling with an in-memory time window and SQLite fingerprint deduplication.
- Vendor-neutral configuration-change detector with reason and matched regex persisted per event.
- SQLite event metadata, backward-compatible startup column migration, Telegram retry, paginated event API and Graylog connection test API.
- React dashboard/events view auto-refreshing through TanStack Query.
- Windows Syslog UDP scripts for Graylog port `1514`.

## Current architecture

`PowerShell Syslog UDP → Graylog → FastAPI poller → detector → SQLite / Telegram → React dashboard`.

## Run and test

1. Start Graylog with a Syslog UDP input on port `1514`.
2. Configure and start backend/frontend as described in `README.md`.
3. Run `powershell -ExecutionPolicy Bypass -File .\scripts\send-test-config-change.ps1`.
4. Verify Graylog, backend logs, SQLite, Telegram and dashboard.

## Required environment configuration

Edit only `backend/.env`: Graylog URL/credentials/query, Telegram enable/token/chat ID, database URL and CORS origins. For Docker Desktop with Graylog published from a separate compose project, set `GRAYLOG_URL=http://host.docker.internal:9000`.

## Extension points

Add vendor-specific patterns in `backend/app/services/detector.py`, enrich Graylog normalization, add database migrations, and add authenticated UI/API access when moving beyond an MVP.
