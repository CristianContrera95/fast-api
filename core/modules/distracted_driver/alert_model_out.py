from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AlertModelOut(BaseModel):
    id: str
    edge_device_id: str
    edge_device_name: Optional[str] = None
    truck_id: int
    use_case: str
    priority: str

    # Use Case Alert specific
    event_start: datetime
    event_end: Optional[datetime] = None
    status: str
    behavior: str
