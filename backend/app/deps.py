import uuid
from typing import Generator

from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Device, Settings


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_device(db: Session, device_id: str) -> Device:
    """Upsert a Device + default Settings row. Shared by all routers."""
    device = db.get(Device, device_id)
    if device is None:
        device = Device(id=device_id)
        db.add(device)
        db.add(Settings(device_id=device_id))
        db.commit()
    elif db.get(Settings, device_id) is None:
        db.add(Settings(device_id=device_id))
        db.commit()
    return device


def get_device_id(x_device_id: str | None = Header(default=None)) -> str:
    if not x_device_id:
        raise HTTPException(status_code=400, detail="Missing X-Device-Id header")
    try:
        uuid.UUID(str(x_device_id))
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Invalid X-Device-Id header")
    return x_device_id
