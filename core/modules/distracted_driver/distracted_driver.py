from datetime import datetime
from typing import List

from bson import ObjectId
from sqlalchemy.orm import Session

from app import logger
from core.modules.modules import ModuleInterface
from db.mongodb import edge_device_mongo, event_mongo, frames_mongo
from db.mongodb.event_record import EventRecord
from models import event_model, account_model
from models.event_model import Event, EventType
from models.use_case_model import UseCaseModel
from .alert_behaviors import AlertBehaviors
from ...event_core import EventVerificationResult

from ...file_upload_core import upload_image
from ...job_core import done_job
from ...message_queues import message_queues
from .alert_record import AlertRecord, AlertStatus
from .components import generate_driver_safety_component

MAX_FRAMES_PER_ALERT = 20


class DistractedDriver(ModuleInterface):
    def __init__(self):
        pass

    alert_filter = {"category": UseCaseModel.driver_safety, "event.type": AlertRecord.alert_type}

    def generate_component(self, db: Session, component, filters=None):
        return generate_driver_safety_component(db, component, filters)

    def get_classes(self) -> List[str]:
        return [c.value for c in AlertBehaviors]

    def verify_event(self, event_id: str, verification_data: event_model.EventVerification, event,
                     account: account_model.Account):
        current_behavior = event['payload']['behavior']
        return event_mongo.update_event({"_id": ObjectId(event_id),
                                         "payload.behavior": verification_data.classification,
                                         "verification": {
                                             "result": EventVerificationResult.confirmed if current_behavior == verification_data.classification else EventVerificationResult.corrected,
                                             "user": account.email}})

    def new_event(self, db: Session, event):
        logger.info("NEW EVENT ON DISTRACTED DRIVER USE CASE")
        if event.type == EventType.event_basic:
            logger.info("type: event basic")
            return self.basic_event(event)
        elif event.type == EventType.keep_alive:
            # Logic to keep alive event
            logger.info("type: keep alive")
            if "current_state" in vars(event):
                logger.info(
                    f"Edge device: {event.edge_device_uid}, current state: {event.current_state}, last update: {event.last_update}"
                )
                self.check_alert_state_consistency(event.current_state, event.edge_device_uid)
            # Get all messages for edge device from its queue
            messages = message_queues.get_all_messages(event.edge_device_uid)
            return messages
        elif event.type == EventType.init:
            # logic to init
            logger.info("type: init")
            return self.init_event(event)
        elif event.type == EventType.start_alert:
            # logic to start alert
            logger.info("type: start alert")
            return self.start_alert(event)
        elif event.type == EventType.end_alert:
            # logic to end alert
            logger.info("type: end alert")
            return self.end_alert(event)
        elif event.type == EventType.send_frames:
            # logic to send frames
            logger.info("type: send frames")
            return self.receive_frames(event)
        elif event.type == EventType.send_safe_frames:
            # logic to send safe frames
            logger.info("type: send safe frames")
            return self.save_safe_frame(event)  # frames_mongo.new_frame_record(event.dict(exclude_unset=True))
        elif event.type == EventType.send_status:
            # logic to send status
            logger.info("type: send status")
            return event_mongo.new_event(event.dict(exclude_unset=True))
        elif event.type == EventType.worker_event:
            # logic to worker event
            logger.info("type: worker event")
            return self.worker_event(event)
        else:
            raise ValueError(f"{type} is not a valid type event")

    def check_alert_state_consistency(self, edge_device_id, alert_state):
        if alert_state == AlertBehaviors.safe:  # TODO: Create alert if needed
            logger.info("Device reported safe state, closing all active alerts of device.")
            close_all_alerts_from_edge_device(edge_device_id)

    def basic_event(self, event: Event):
        # logic to event basic
        mongo_document = EventRecord(event)

        """This means that if there was an open alert, it should be closed now, since it is no longer open"""
        close_all_alerts_from_edge_device(event.edge_device_uid, mongo_document.timestamp)

        event = event_mongo.new_event(vars(mongo_document))
        logger.info(f"Created event of id: {str(event['_id'])}")
        return event

    def init_event(self, event: Event):

        """This means that if there was an open alert, it should be closed now, since it is no longer open"""
        close_all_alerts_from_edge_device(event.edge_device_uid, event.timestamp)

        event_mongo.new_event(event.dict(exclude_unset=True))

        edge_device = edge_device_mongo.get_edge_device(event.edge_device_uid)
        if "settings" not in edge_device.keys():
            logger.info("No settings configured for the edge device")
            return None
        return edge_device["settings"]

    def start_alert(self, event: Event):
        # Create alert event.
        mongo_document = AlertRecord(event)

        """ Before creating new alert, close all open ones,
        there should be only one open alert per edge device, at any given time. """
        close_all_alerts_from_edge_device(event.edge_device_uid, mongo_document.timestamp)

        alert = event_mongo.new_event(vars(mongo_document))
        logger.info(f"Created alert of id: {alert}")
        return alert

    def end_alert(self, event: Event):
        active_alert = get_active_alert_from_edge_device(event.edge_device_uid)

        if active_alert is None:
            logger.error("There is no active alert for edge device.")
            return "error, no active alert"

        active_alert["payload"]["status"] = AlertStatus.ended
        active_alert["payload"]["event_end"] = event.timestamp
        ended = event_mongo.update_event(active_alert)
        logger.info(f"Updated alert successfully. {ended}")
        if ended is not None:
            ended["_id"] = str(ended["_id"])
        return ended

    def receive_frames(self, event: Event):
        active_alert = get_active_alert_from_edge_device(event.edge_device_uid)

        if active_alert is None:
            logger.error("There is no active alert for edge device. Can't associate frame")
            return "error, no active alert"

        frame_url = upload_image(event.frame)

        frames_mongo.new_frame_record(
            {"behavior": active_alert["payload"]["behavior"], "timestamp": event.timestamp, "storage": frame_url}
        )

        frame_position = len(active_alert["frames"]) + 1

        if frame_position <= MAX_FRAMES_PER_ALERT:
            active_alert["frames"].append(
                {"position": frame_position, "timestamp": event.timestamp, "storage": frame_url}
            )
            updated = event_mongo.update_event(active_alert)

            if updated is not None:
                logger.info(f"Added frame {frame_url} in position {frame_position} to alert {str(active_alert['_id'])}")
                updated["_id"] = str(updated["_id"])
            return updated

        logger.error("Max frames per alert reached")
        return "Max frames per alert reached"

    def save_safe_frame(self, event: Event):

        frame_url = upload_image(event.frame)

        new_frame_id = frames_mongo.new_frame_record(
            {"behavior": "Safe", "timestamp": event.timestamp, "storage": frame_url}
        )
        logger.info(f"Saved new safe frame: {new_frame_id}, url: {frame_url}")
        return new_frame_id

    def worker_event(self, event: Event):
        # logic to event basic
        mongo_document = EventRecord(event)
        mongo_document.worker_record(event)

        event_return = event_mongo.new_event(vars(mongo_document))

        # update job to done
        if done_job(event.job_id, event.worker_id):
            logger.info("Update job to done")
        else:
            logger.info("Error in update job to done")
        logger.info(f"Created worker event of id: {str(event_return)}")

        return event


def get_active_alert_from_edge_device(edge_device_id):
    query_filters = {
        **DistractedDriver.alert_filter,
        "origin.edge_device_id": edge_device_id,
        "payload.status": AlertStatus.ongoing,
    }
    return event_mongo.get_last_event(query_filters)


def close_all_alerts_from_edge_device(edge_device_id, end_time=datetime.now()):
    logger.info(f"Closing all active alerts from device {edge_device_id}")
    query_filters = {
        **DistractedDriver.alert_filter,
        "origin.edge_device_id": edge_device_id,
        "payload.status": AlertStatus.ongoing,
    }
    update_fields = {"payload.event_end": end_time, "payload.status": AlertStatus.ended}
    return event_mongo.update_events(query_filters, update_fields)
