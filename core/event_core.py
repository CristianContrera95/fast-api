import logging
from collections import Counter
from datetime import datetime as dt
from enum import Enum

from bson import ObjectId
from sqlalchemy.orm import Session

from db.mongodb import edge_device_mongo, event_mongo
from models import event_model, account_model

from .edge_device_core import update_last_interaction
from .modules.modules import ModuleFactory
from .utils.query_params import exclude_none_keys

logger = logging.getLogger(__name__)


class EventVerificationResult(str, Enum):
    corrected = "corrected"
    confirmed = "confirmed"


def get_event(id="0"):
    var_event = event_mongo.get_event(id)
    if var_event is None:
        logger.error("error, event not found")
        return "error, event not found"
    return var_event


def get_all_event(query_params: dict = {}, filter_params: dict = {}):
    filter_params = exclude_none_keys(filter_params)

    limit = query_params.get("limit", None)
    skip = query_params.get("skip", None)

    sort_by, sort_order = query_params.get("sort_by"), query_params.get("sort_order")
    sort_fields = []
    if sort_by is not None:
        sort_fields.append((sort_by, sort_order))

    return {
        "events": event_mongo.get_all_events(offset=skip, limit=limit, filters=filter_params, sort_fields=sort_fields),
        "pagination": {"total_rows": event_mongo.count(filters=filter_params), "skip": skip, "limit": limit},
    }


def get_event_classifications(use_case: str):
    use_case = ModuleFactory.create_module(use_case)
    return use_case.get_classes()


def verify_event(event_id: str, verification_data: event_model.EventVerification, account: account_model.Account):
    event = event_mongo.get_event(event_id)
    use_case = ModuleFactory.create_module(event['category'])
    verification_result = use_case.verify_event(event_id, verification_data, event, account)
    logger.info("Verified successfully")
    return verification_result


def new_event(db: Session, event: event_model.Event):
    logger.info(f"new event: {[(key, value) for key, value in event.dict().items() if key != 'frame']}")
    found = False
    if event.edge_device_uid is not None and event.truck_id is not None:
        found = True
        logger.info(f"the new event is a edge_device {event.edge_device_uid}")
        edge_device = edge_device_mongo.get_edge_device(event.edge_device_uid)
        if edge_device is None:
            logger.error("error, edge device not found")
            return "error, edge device not found"
        update_last_interaction(db, event.edge_device_uid)
    elif event.worker_id is not None:
        found = True
        logger.info(f"the new event is a worker {event.worker_id}")

    if not found:
        raise Exception("Not found origen, is necessary edge_device_uid and truck_id, or worker_id")

    use_case = ModuleFactory.create_module(event.use_case)
    return use_case.new_event(db, event)


def get_event_resume_by_truck(truck_id: int = 0):
    events = list(event_mongo.get_events_by_truck(truck_id))

    if not events:
        return {
            "id": truck_id,
            "lastAlert": "-",
            "lastAlertDate": "never",
            "isHappeningNow": False,
            "recurringAlert": "-",
            "currentDriver": "-",
            "alertsToday": False,
        }
    recurring_alert = Counter(map(lambda x: x["payload"]["behavior"], events)).most_common(1)[0][0]
    alerts_today = len(list(filter(lambda x: x["last_update"].date() == dt.date(dt.now()), events)))

    return {
        "id": truck_id,
        "lastAlert": events[0]["payload"]["behavior"],
        "lastAlertDate": events[0]["timestamp"],
        "isHappeningNow": events[0]["payload"]["status"] != "ended",
        "recurringAlert": recurring_alert,
        "currentDriver": "-",
        "alertsToday": alerts_today,
    }
