from typing import Optional

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.auth import auth
from api.auth.auth import validate_api_client_id
from api.handlers.common import CommonQueryParams
from api.handlers.http_errors import handle_exception
from app.sqlserverdb import get_db
from core import event_core
from models import event_model
from models.account_model import Account

router = APIRouter()


class EventFilterParams:
    def __init__(
            self,
            event_type: Optional[str] = Query(None, description="Type of event"),
            priority: Optional[str] = Query(None, description="Priority of event"),
            behavior: Optional[str] = Query(None, description="Behavior of alert if looking by alert"),
            edge_device_id: Optional[str] = Query(None, description="Id of edge device"),
            truck_id: Optional[str] = Query(None, description="Id of truck"),
            status: Optional[str] = Query(None, description="Status of event"),
            id: Optional[str] = Query(None, description="ID of event"),
    ):
        self.event_type = event_type
        self.id = id
        self.priority = priority
        self.behavior = behavior
        self.edge_device_id = edge_device_id
        self.truck_id = truck_id
        self.status = status


@router.get("/")
def get_all_event(
        query: CommonQueryParams = Depends(CommonQueryParams),
        filters: EventFilterParams = Depends(EventFilterParams),
        _: Account = Depends(auth.get_current_account),
):
    return event_core.get_all_event(query_params=query.__dict__, filter_params=filters.__dict__)


@router.get("/classes/{use_case}")
def get_event(use_case: str, _: Account = Depends(auth.get_current_account)):
    return {"classes": event_core.get_event_classifications(use_case)}


@router.put("/verify/{event_id}")
def get_event(event_id: str, verification_data: event_model.EventVerification, account: Account = Depends(auth.get_current_account)):
    updated = event_core.verify_event(event_id, verification_data, account)
    return {"event": updated}


@router.get("/{event_id}")
def get_event(event_id: str, _: Account = Depends(auth.get_current_account)):
    if ObjectId.is_valid(event_id):
        one_event = event_core.get_event(event_id)
        return {"event": one_event}
    else:
        return {"event": "event_id not valid"}


@router.post("/")
def new_event(event: event_model.Event, db: Session = Depends(get_db), _=Depends(validate_api_client_id)):
    try:
        event = event_core.new_event(db, event)
        return {"event": event}

    except Exception as e:
        handle_exception(e)
