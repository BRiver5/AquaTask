from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..deps import ensure_device, get_db, get_device_id
from ..models import Settings, WaterEntry
from ..schemas import EntryCreate, EntryRead, TodayRead

router = APIRouter(prefix="/entries", tags=["entries"])


def _local_date_expr(tz_offset_min: int):
    """SQLite date() of logged_at shifted into the device's local timezone."""
    return func.date(WaterEntry.logged_at, f"{tz_offset_min} minutes")


@router.post("", response_model=EntryRead, status_code=201)
def create_entry(
    payload: EntryCreate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    ensure_device(db, device_id)
    entry = WaterEntry(
        device_id=device_id,
        amount_ml=payload.amount_ml,
        logged_at=payload.logged_at or datetime.now(timezone.utc),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_entry(
    entry_id: int,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    entry = db.get(WaterEntry, entry_id)
    if entry is None or entry.device_id != device_id:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return Response(status_code=204)


@router.get("/today", response_model=TodayRead)
def today(
    tz_offset_min: int = Query(default=0, ge=-840, le=840),
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    ensure_device(db, device_id)
    settings = db.get(Settings, device_id)

    local_now = datetime.now(timezone.utc) + timedelta(minutes=tz_offset_min)
    local_today = local_now.date().isoformat()

    date_expr = _local_date_expr(tz_offset_min)
    entries = (
        db.query(WaterEntry)
        .filter(WaterEntry.device_id == device_id, date_expr == local_today)
        .order_by(WaterEntry.logged_at.desc())
        .all()
    )
    total = sum(e.amount_ml for e in entries)
    return TodayRead(
        entries=entries,
        total_ml=total,
        goal_ml=settings.daily_goal_ml,
    )
