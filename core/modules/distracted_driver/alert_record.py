"""Data structure for event document in mongo's Events Collection (See docs)"""
from enum import Enum

from db.mongodb.event_record import EventRecord
from models import event_model


class AlertRecord(EventRecord):
    alert_type = "alert"

    def __init__(self, event: event_model.Event):
        super().__init__(event)
        self.payload = {
            "event_start": event.timestamp,
            "event_end": None,
            "status": "ongoing",
            "confidence": 0,  # TODO: Include
            "behavior": event.behavior,
        }
        self.event["type"] = AlertRecord.alert_type

        self.frames = []


class AlertStatus(str, Enum):
    ongoing = "ongoing"
    ended = "ended"
