# Firewall Config Monitor

MVP theo dõi thay đổi cấu hình cho nhiều loại tường lửa. Ứng dụng không kết nối trực tiếp tới thiết bị; mọi log đều đi qua Graylog.

```text
Firewall / simulated GELF message → Graylog → FastAPI polling → SQLite / Telegram
                                                    ↓ REST API
                                             React + Vite + Tailwind
```

## Architecture

- `backend/`: FastAPI, Graylog polling, detector theo pattern, SQLite, Telegram và tests.
- `frontend/`: React 19, TypeScript, Vite, TailwindCSS, Axios, React Router, TanStack Query và Lucide icons.
- `GRAYLOG_SEARCH_QUERY` chỉ chọn log đầu vào; detector quyết định log nào là thay đổi cấu hình. Giá trị mặc định `*` cho phép theo dõi nhiều firewall.
- Docker frontend Nginx phục vụ SPA tại cổng `5173` và proxy `/api/*` đến `backend:8000`.

## Development

```powershell
Copy-Item backend/.env.example backend/.env
Set-Location backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Terminal khác:

```bash
cd frontend
npm install
npm run dev
```

Mở http://localhost:5173; Swagger ở http://localhost:8000/docs. Điền URL, username/password Graylog trong `backend/.env`. Khi backend chạy trực tiếp trên Windows và Graylog compose publish `9000:9000`, dùng `GRAYLOG_URL=http://localhost:9000`. `MOCK_GRAYLOG=true` chỉ dành cho smoke test không có Graylog.

## Demo: gửi log mô phỏng từ Windows đến Graylog

Compose Graylog bạn cung cấp hiện publish `12201/udp`, phù hợp **GELF UDP**. Trước tiên mở Graylog tại http://localhost:9000, vào **System / Inputs**, chọn **GELF UDP**, chọn node rồi bấm **Launch new input** với port `12201`.

Giữ ứng dụng backend chạy, sau đó mở PowerShell và gửi một GELF message mô phỏng configuration change:

```powershell
$payload = @{ version = '1.1'; host = 'demo-firewall-01'; short_message = 'Administrator executed configuration change: created rule allow-https'; level = 4; _device_type = 'firewall'; _source_ip = '192.168.1.1' } | ConvertTo-Json -Compress
$client = [System.Net.Sockets.UdpClient]::new()
$bytes = [Text.Encoding]::UTF8.GetBytes($payload)
[void]$client.Send($bytes, $bytes.Length, '127.0.0.1', 12201)
$client.Dispose()
```

Kiểm tra message trong Graylog Search. Trong tối đa một chu kỳ `POLL_INTERVAL_SECONDS` (mặc định 5 giây), FastAPI sẽ thấy log, detector nhận keyword `configuration change`, lưu event vào SQLite, gửi Telegram nếu cấu hình, rồi React dashboard tự refresh. Source trên giao diện thường là `demo-firewall-01`; field `_source_ip` còn trong Raw Graylog Data.

Nếu muốn gửi Syslog UDP chuẩn thay vì GELF, hãy tạo **Syslog UDP input** trong Graylog và thêm một mapping UDP khác (ví dụ `5140:5140/udp`) vào compose Graylog; compose hiện tại chưa publish một cổng Syslog UDP chuẩn.

## Docker

```bash
cp backend/.env.example backend/.env
docker compose build
docker compose up -d
docker compose ps
```

Mở http://localhost:5173. Kiểm tra Nginx-to-FastAPI proxy tại http://localhost:5173/api/status; Swagger backend ở http://localhost:8000/docs. Docker frontend phải gọi `backend:8000`, không phải `localhost:8000`.

Graylog của bạn chạy trong một compose riêng và publish cổng trên Windows host. Vì vậy trước khi chạy compose của ứng dụng này, đặt trong `backend/.env`:

```env
GRAYLOG_URL=http://host.docker.internal:9000
```

`localhost:9000` bên trong container backend trỏ về chính container backend, không phải Graylog. `host.docker.internal` là hostname Docker Desktop dành cho Windows host.

## Testing and troubleshooting

```bash
cd backend && pytest
cd frontend && npm run build
```

- Không thấy demo log trong Graylog: xác nhận GELF UDP input đang chạy và Docker Desktop publish `12201/udp`.
- Graylog có log nhưng dashboard chưa có event: kiểm tra `GRAYLOG_SEARCH_QUERY`, endpoint/API credentials và nội dung log phải khớp pattern trong `backend/app/services/detector.py`.
- Frontend không gọi backend: kiểm tra Vite proxy, backend port 8000 và `CORS_ORIGINS`.
- Telegram lỗi: kiểm tra `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID`.

Detector hiện dùng keyword/regex đơn giản để phù hợp demo. Khi có log thật từ từng vendor, bổ sung pattern có kiểm soát trong `ConfigChangeDetector`; không cần thay kiến trúc hay giới hạn hệ thống vào một loại firewall.
