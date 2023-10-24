from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from .use_case_model import UseCaseModel


class EventType(str, Enum):
    event_basic = "event_basic"
    keep_alive = "keep_alive"
    init = "init"
    alert = "alert"
    start_alert = "start_alert"
    end_alert = "end_alert"
    send_frames = "send_frames"
    send_safe_frames = "send_safe_frames"
    send_status = "send_status"
    worker_event = "worker_event"


class Event(BaseModel):
    class Config:
        extra = "allow"

    edge_device_uid: Optional[str]  # optional
    truck_id: Optional[int]  # optional
    worker_id: Optional[str]  # optional
    job_id: Optional[str]  # optional
    priority: str  # optional
    use_case: UseCaseModel  # obligatory
    timestamp: datetime  # obligatory
    verification: Optional[dict]
    # name: str #obligatory
    type: EventType  # obligatory
    is_offer: Optional[bool] = None  # optional



class EventVerification(BaseModel):
    classification: str
