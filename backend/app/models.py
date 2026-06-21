from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Device(Base):
    __tablename__ = "device"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=utcnow)


class Settings(Base):
    __tablename__ = "settings"

    device_id = Column(String, ForeignKey("device.id"), primary_key=True)
    daily_goal_ml = Column(Integer, default=2000, nullable=False)
    theme_color = Column(String, default="#2196F3", nullable=False)
    container_icon = Column(String, default="glass", nullable=False)
    reminders_enabled = Column(Boolean, default=False, nullable=False)
    reminder_interval_min = Column(Integer, nullable=True)
    reminder_start = Column(String, nullable=True)
    reminder_end = Column(String, nullable=True)


class WaterEntry(Base):
    __tablename__ = "water_entry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("device.id"), index=True, nullable=False)
    amount_ml = Column(Integer, nullable=False)
    logged_at = Column(DateTime, default=utcnow, index=True, nullable=False)
