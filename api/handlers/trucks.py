from typing import Dict, Optional

from fastapi import APIRouter, Depends

from api.auth import auth
from core import edge_device_core, event_core
from models.account_model import Account

router = APIRouter()


@router.get("/")
def get_all_trucks(params: Optional[Dict] = None, current_account: Account = Depends(auth.get_current_account)):
    """ return list[truck_id] """
    if params is not None:
        skip = params.get("skip")
        limit = params.get("limit")
        all_trucks = edge_device_core.get_all_trucks(skip, limit)
    else:
        all_trucks = edge_device_core.get_all_trucks()
    return {"trucks": all_trucks}


@router.get("/{truck_id}/resume")
def resume_truck_id(
    truck_id: int, params: Optional[str] = None, current_account: Account = Depends(auth.get_current_account)
):
    resume = event_core.get_event_resume_by_truck(truck_id)
    return {"trucks_resume": resume}
