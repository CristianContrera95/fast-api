from typing import Optional

from pydantic import BaseModel


class EdgeDevice(BaseModel):
    class Config:
        extra = "allow"

    type: Optional[str] = None
    ip: Optional[str] = None
    port: Optional[str] = None
    status: Optional[str] = None
    last_interaction: Optional[str] = None
    sw_version: Optional[str] = None
    settings: Optional[dict] = None
    sensors: Optional[list] = None
