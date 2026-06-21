# AquaTask Backend

FastAPI + SQLAlchemy + SQLite REST API for the AquaTask water tracker. No accounts;
each client is identified by an anonymous UUID sent in the `X-Device-Id` header.

## Run

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For the Android emulator, the host machine is reachable at `http://10.0.2.2:8000`.
For a physical device, use the host's LAN IP (e.g. `http://192.168.1.x:8000`).

Interactive docs: http://127.0.0.1:8000/docs

## Endpoints

All endpoints require the `X-Device-Id` header (a UUID). The device row and its
default settings are created automatically on first contact.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| POST | `/devices/register` | Idempotently create device + default settings |
| GET | `/settings` | Read settings |
| PUT | `/settings` | Update goal / theme / icon / reminder config |
| POST | `/entries` | Log water: `{ "amount_ml": 250 }` |
| DELETE | `/entries/{id}` | Delete an entry (must belong to the device) |
| GET | `/entries/today?tz_offset_min=180` | Today's entries + total + goal |
| GET | `/history?range=daily\|weekly\|monthly&tz_offset_min=180` | Aggregated buckets |

`tz_offset_min` is the device's UTC offset in minutes (e.g. `+180` for UTC+3) so the
server can group entries by the user's local calendar day.
