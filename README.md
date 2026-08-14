# ASA Config Monitor

MVP theo dõi thay đổi cấu hình Cisco ASA.

```text
Cisco ASA → Syslog → Graylog → FastAPI → SQLite / Telegram
                                      ↓ REST API
                               React + Vite + Tailwind
```

## Architecture

- `backend/`: FastAPI, Graylog polling, detector, SQLite, Telegram và tests.
- `frontend/`: React 19, TypeScript, Vite, TailwindCSS, Axios, React Router, TanStack Query và Lucide icons.
- Trong Docker, Nginx của frontend phục vụ SPA tại cổng `5173` và proxy `/api/*` đến `backend:8000`.

Frontend không bao giờ kết nối trực tiếp tới ASA hoặc Graylog; chỉ gọi FastAPI API.

## Development

Backend:

```powershell
Copy-Item backend/.env.example backend/.env
Set-Location backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Linux/macOS activation: `source .venv/bin/activate`.

Frontend (terminal khác):

```bash
cd frontend
npm install
npm run dev
```

Mở http://localhost:5173. Vite proxy các request `/api` tới `http://localhost:8000`; Swagger vẫn ở http://localhost:8000/docs. Để demo không cần thiết bị thật, đặt `MOCK_GRAYLOG=true` và `ENABLE_TELEGRAM=false` trong `backend/.env`.

## Docker

```bash
cp backend/.env.example backend/.env
docker compose build
docker compose up -d
docker compose ps
```

Mở http://localhost:5173. Kiểm tra Nginx-to-FastAPI proxy tại `http://localhost:5173/api/status`; backend docs (được expose để debug) ở http://localhost:8000/docs.

Docker frontend phải proxy tới `backend:8000`, không phải `localhost:8000`. Backend container cần route/firewall phù hợp để đến `http://192.168.10.10:9000`.

## Testing and troubleshooting

```bash
cd backend && pytest
cd frontend && npm run build
```

- Frontend không gọi được backend: kiểm tra backend cổng 8000, Vite proxy và `CORS_ORIGINS` (mặc định `http://localhost:5173`).
- Docker frontend không gọi được backend: kiểm tra `frontend/nginx.conf`, đặc biệt upstream `backend:8000`.
- Graylog không kết nối: kiểm tra URL, API endpoint phù hợp version Graylog, routing/firewall tới `192.168.10.10:9000`.
- Telegram lỗi: kiểm tra `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID`.

`ConfigChangeDetector` tại `backend/app/services/detector.py` cần được tinh chỉnh bằng log ASA thực tế. Khi Graylog hoặc Telegram lỗi, FastAPI vẫn chạy và polling tiếp tục; fingerprint trong SQLite chặn alert trùng lặp.
