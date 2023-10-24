from datetime import datetime

from models import event_model


class EventRecord:
    def clean_origin(self, event):
        if event.worker_id is not None:
            return {
                "worker_id": event.worker_id,
                "job_id": event.job_id,
            }
        elif event.edge_device_uid is not None:
            return {"edge_device_id": event.edge_device_uid, "truck_id": event.truck_id}
        return {}

    def __init__(self, event: event_model.Event):
        self.category = event.use_case
        self.event = {"type": event.type, "priority": event.priority}
        self.timestamp = event.timestamp
        self.insert_timestamp = None
        self.last_update = None

        self.origin = self.clean_origin(event)

        self.payload = {}

    def worker_record(self, event: event_model.Event):
        self.category = event.use_case
        self.event = {"type": event.type, "priority": event.priority}
        self.timestamp = event.timestamp
        self.insert_timestamp = None
        self.last_update = datetime.now()

        self.origin = self.clean_origin(event)

        self.payload = event.payload
