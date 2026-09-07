# Firewall Config Monitor

Local MVP theo dõi thay đổi cấu hình từ nhiều loại firewall. Ứng dụng không nhận log trực tiếp; Graylog là điểm nhận Syslog và FastAPI poll Graylog REST API.

```text
PowerShell Syslog Simulator / Firewall
              ↓ UDP 1514
            Graylog
              ↓ REST API polling
 FastAPI → Detector → SQLite → Telegram
              ↓
       React dashboard
```

## Project structure

```text
backend/       FastAPI, Graylog client/poller, detector, SQLite, Telegram, tests
frontend/      React + Vite + Tailwind dashboard
scripts/       Windows Syslog UDP simulation scripts
```

## Prerequisites

- Python 3.12+
- Node.js 22+ and npm
- Docker Desktop for Graylog and optional app containers
- A running Graylog with a **Syslog UDP Input** listening on UDP port `1514`

## Graylog configuration (Docker Desktop Windows)

Your separate Graylog compose must publish the input port:

```yaml
ports:
  - "9000:9000"
  - "1514:1514/udp"
```

In Graylog Web UI at http://localhost:9000, open **System → Inputs**, launch a **Syslog UDP** input on port `1514`, then confirm it is running. This is Syslog UDP, not GELF.

## Environment

Copy `backend/.env.example` to `backend/.env` and configure only that file.

```env
# When backend runs directly on Windows
GRAYLOG_URL=http://localhost:9000

# Use a valid Graylog account
GRAYLOG_USERNAME=admin
GRAYLOG_PASSWORD=CHANGE_ME
GRAYLOG_SEARCH_QUERY=*
POLL_INTERVAL_SECONDS=5

TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

When backend runs in this project's Docker Compose but Graylog runs in a separate Docker Desktop compose, use `GRAYLOG_URL=http://host.docker.internal:9000`. Do not use `localhost:9000` inside the backend container.

## Development

Start backend:

```powershell
Copy-Item backend/.env.example backend/.env
Set-Location backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Start frontend in another terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open http://localhost:5173. API documentation is available at http://localhost:8000/docs.

## End-to-end Syslog test

1. Start Graylog and verify its Syslog UDP input is running on `1514`.
2. Start backend and frontend.
3. In the repository root, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\send-test-config-change.ps1
```

The script sends this Syslog-compatible message to `127.0.0.1:1514`:

```text
<134>Aug 31 14:30:00 TEST-FIREWALL configuration change: created firewall rule allow-https
```

4. Confirm the message in Graylog Search.
5. Within the polling interval (normally five seconds), the backend logs a detected configuration change, stores one event in SQLite and sends Telegram if enabled.
6. Dashboard auto-refresh displays the event without a browser reload.

For a custom simulation:

```powershell
.\scripts\send-graylog.ps1 -Message "configuration change: updated outbound NAT rule"
```

## API

- `GET /api/health`
- `GET /api/status`
- `GET /api/events?limit=50&offset=0` returns `{ items, total }`
- `GET /api/events/{event_id}`
- `POST /api/test/graylog`
- `POST /api/test/telegram`

## Docker application services

```powershell
Copy-Item backend/.env.example backend/.env
# Set GRAYLOG_URL=http://host.docker.internal:9000 in backend/.env
docker compose build
docker compose up -d
```

The React/Nginx dashboard is http://localhost:5173; Nginx proxies `/api/*` to the backend container. The backend port is exposed at `8000` only for API/debug access. Graylog remains in its own compose project.

## Test commands

```powershell
Set-Location backend
pytest

Set-Location ..\frontend
npm run build
```

## Troubleshooting

- Graylog receives Syslog but no dashboard event: check FastAPI logs, Graylog credentials, `GRAYLOG_SEARCH_QUERY`, and whether the message contains a detection pattern such as `configuration change`.
- Backend cannot reach Graylog in Docker: use `host.docker.internal:9000` and check Docker Desktop is running.
- Syslog not received: confirm both the Docker UDP mapping and Graylog Syslog UDP input use `1514`.
- Telegram fails: set `TELEGRAM_ENABLED=true`, token and chat ID in `backend/.env`. Failures do not stop polling or database storage.

Detection patterns live in `backend/app/services/detector.py`. Add vendor-specific patterns from actual logs there; the monitor itself is vendor-neutral.
