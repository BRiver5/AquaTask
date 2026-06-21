# AquaTask

> The most refreshing task of your day.

A simple, no-login water and habit tracker. AquaTask is a monorepo with a FastAPI
backend and an Expo (React Native) mobile app. There is no sign-up: each device is
identified by an anonymous, randomly generated ID, and only water-log amounts and
timestamps are stored.

## Layout

| Folder | Description |
|--------|-------------|
| [`backend/`](backend) | FastAPI + SQLAlchemy + SQLite REST API |
| [`mobile/`](mobile) | Expo SDK 54 React Native app (Expo Router, TypeScript) |

## Quick start

1. Start the backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. Start the app (in a second terminal):

```bash
cd mobile
npm install
npx expo start
```

By default the app talks to `http://10.0.2.2:8000` (the Android emulator's route to
the host machine). Override it with `EXPO_PUBLIC_API_URL` in `mobile/.env` for a
physical device. See each subfolder's README for details.

## Privacy

No accounts, no personal data, no third-party trackers or ads. The app stores only
an anonymous device ID plus your water-log amounts and timestamps. Reinstalling or
clearing app data generates a new anonymous ID.
