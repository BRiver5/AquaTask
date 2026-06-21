from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..deps import ensure_device, get_db, get_device_id
from ..models import Settings, WaterEntry
from ..schemas import HistoryPoint, HistoryRead

router = APIRouter(prefix="/history", tags=["history"])

RANGE_DAYS = {"daily": 7, "weekly": 56, "monthly": 180}


@router.get("", response_model=HistoryRead)
def history(
    range: str = Query(default="daily", pattern="^(daily|weekly|monthly)$"),
    tz_offset_min: int = Query(default=0, ge=-840, le=840),
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    rng = range
    ensure_device(db, device_id)
    settings = db.get(Settings, device_id)
    goal = settings.daily_goal_ml

    days = RANGE_DAYS.get(rng, 7)
    local_now = datetime.now(timezone.utc) + timedelta(minutes=tz_offset_min)
    today = local_now.date()
    start_local = (today - timedelta(days=days - 1)).isoformat()

    date_expr = func.date(WaterEntry.logged_at, f"{tz_offset_min} minutes")
    rows = (
        db.query(date_expr.label("day"), func.sum(WaterEntry.amount_ml).label("total"))
        .filter(WaterEntry.device_id == device_id, date_expr >= start_local)
        .group_by(date_expr)
        .all()
    )
    by_day = {row.day: int(row.total or 0) for row in rows}

    if rng == "daily":
        points = _bucket_daily(by_day, today, days, goal)
    elif rng == "weekly":
        points = _bucket_weekly(by_day, today, goal)
    else:
        points = _bucket_monthly(by_day, today, goal)

    return HistoryRead(points=points)


def _point(day: str, total: int, goal: int) -> HistoryPoint:
    percent = int(round((total / goal) * 100)) if goal else 0
    return HistoryPoint(date=day, total_ml=total, goal_ml=goal, percent=percent)


def _bucket_daily(by_day, today, days, goal) -> list[HistoryPoint]:
    points: list[HistoryPoint] = []
    for i in range(days):
        day = (today - timedelta(days=days - 1 - i)).isoformat()
        points.append(_point(day, by_day.get(day, 0), goal))
    return points


def _bucket_weekly(by_day, today, goal) -> list[HistoryPoint]:
    points: list[HistoryPoint] = []
    monday = today - timedelta(days=today.weekday())
    for w in range(7, -1, -1):
        week_start = monday - timedelta(weeks=w)
        total = sum(
            by_day.get((week_start + timedelta(days=d)).isoformat(), 0)
            for d in range(7)
        )
        week_goal = goal * 7
        percent = int(round((total / week_goal) * 100)) if week_goal else 0
        points.append(
            HistoryPoint(
                date=week_start.isoformat(),
                total_ml=total,
                goal_ml=week_goal,
                percent=percent,
            )
        )
    return points


def _bucket_monthly(by_day, today, goal) -> list[HistoryPoint]:
    months: list[tuple[int, int]] = []
    y, m = today.year, today.month
    for _ in range(6):
        months.append((y, m))
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    months.reverse()

    totals: dict[str, int] = {}
    for day, total in by_day.items():
        key = day[:7]
        totals[key] = totals.get(key, 0) + total

    points: list[HistoryPoint] = []
    for (yy, mm) in months:
        key = f"{yy:04d}-{mm:02d}"
        total = totals.get(key, 0)
        month_goal = goal * _days_in_month(yy, mm)
        percent = int(round((total / month_goal) * 100)) if month_goal else 0
        points.append(
            HistoryPoint(
                date=f"{key}-01",
                total_ml=total,
                goal_ml=month_goal,
                percent=percent,
            )
        )
    return points


def _days_in_month(year: int, month: int) -> int:
    nxt = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    return (nxt - timedelta(days=1)).day
