from sqlalchemy.orm import Session

from app import logger
from core.modules.modules import ModuleInterface
from db.mongodb import event_mongo
from models.event_model import EventType


class PeopleCounter(ModuleInterface):
    def __init__(self):
        pass

    def new_event(self, db: Session, event):
        logger.info("NEW EVENT ON PEOPLE_COUNTER")
        if event.type == EventType.event_basic:
            # logic to event basic
            logger.info("type: event basic")
            var_event = event_mongo.new_event(event.dict(exclude_unset=True))
        elif event.type == EventType.keep_alive:
            # logic to keep alive
            logger.info("type: keep alive")
            var_event = event_mongo.new_event(event.dict(exclude_unset=True))
        else:
            raise ValueError(f"{type} is not a valid type event")
        if var_event is None:
            return "error, in create event"
        return var_event
