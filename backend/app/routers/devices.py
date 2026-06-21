from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import ensure_device, get_db, get_device_id
from ..schemas import SettingsRead

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/register", response_model=SettingsRead)
def register_device(
    device_id: str = Depends(get_device_id),
    db: Session = Depends(get_db),
):
    """Idempotent: ensures a Device + default Settings row exists."""
    ensure_device(db, device_id)
    from ..models import Settings

    return db.get(Settings, device_id)
