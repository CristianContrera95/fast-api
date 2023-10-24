from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.orm import Session

from models import event_model, account_model
from models.use_case_model import UseCaseModel


class ModuleInterface(ABC):
    @abstractmethod
    def new_event(self, db: Session, event) -> str:
        pass

    @abstractmethod
    def get_classes(self) -> List[str]:
        pass

    @abstractmethod
    def generate_component(self, db: Session, component, filters=None):
        pass

    @abstractmethod
    def verify_event(self, event_id: str, verification_data: event_model.EventVerification, event,
                     account: account_model.Account):
        pass


class ModuleFactory:
    _intance_module: ModuleInterface

    def __init__(
            self,
    ):
        pass

    @classmethod
    def create_module(cls, use_case: str, **config):
        if use_case == UseCaseModel.driver_safety:
            from .distracted_driver.distracted_driver import DistractedDriver

            cls._intance_module = DistractedDriver(**config)
        elif use_case == UseCaseModel.people_counter:
            from .people_counter.people_counter import PeopleCounter

            cls._intance_module = PeopleCounter(**config)
        else:
            raise ValueError(f"{type} is not a valid use case")
        return cls._intance_module
