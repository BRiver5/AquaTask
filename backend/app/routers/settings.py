from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import ensure_device, get_db, get_device_id
from ..models import Settings
from ..schemas import SettingsRead, SettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsRead)
def read_settings(
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    ensure_device(db, device_id)
    return db.get(Settings, device_id)


@router.put("", response_model=SettingsRead)
def update_settings(
    payload: SettingsUpdate,
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    ensure_device(db, device_id)
    settings = db.get(Settings, device_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings
