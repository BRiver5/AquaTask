from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    device_id: str
    daily_goal_ml: int
    theme_color: str
    container_icon: str
    reminders_enabled: bool
    reminder_interval_min: Optional[int] = None
    reminder_start: Optional[str] = None
    reminder_end: Optional[str] = None


class SettingsUpdate(BaseModel):
    daily_goal_ml: Optional[int] = Field(default=None, ge=100, le=20000)
    theme_color: Optional[str] = None
    container_icon: Optional[str] = None
    reminders_enabled: Optional[bool] = None
    reminder_interval_min: Optional[int] = Field(default=None, ge=15, le=720)
    reminder_start: Optional[str] = None
    reminder_end: Optional[str] = None


class EntryCreate(BaseModel):
    amount_ml: int = Field(..., ge=1, le=5000)
    logged_at: Optional[datetime] = None


class EntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount_ml: int
    logged_at: datetime


class TodayRead(BaseModel):
    entries: list[EntryRead]
    total_ml: int
    goal_ml: int


class HistoryPoint(BaseModel):
    date: str
    total_ml: int
    goal_ml: int
    percent: int


class HistoryRead(BaseModel):
    points: list[HistoryPoint]
