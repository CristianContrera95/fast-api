import queue
import time
from enum import Enum

from app import logger
from db.mongodb import edge_device_mongo

QUEUE_SIZE = 512
QUEUE_PUT_TIMEOUT = 10
QUEUE_TTL = 10 * 60  # 10 minutos
QUEUE_NUMBER_OF_ITEMS_TO_REMOVE_WHEN_FULL = 1


class MessageTypes(Enum):
    configuration_change = "configuration_change"
    send_status = "send_status"


class MessageQueues:
    def __init__(self, size, timeout, ttl, items_remove):
        self.size = size
        self.timeout = timeout
        self.ttl = ttl
        self.items_remove = items_remove
        self.queues_dict = {}
        var_edge_device = edge_device_mongo.get_all_edge_device()
        ids = [ed["_id"] for ed in var_edge_device]
        for id in ids:
            self.new_message_queue(id)

    def new_message_queue(self, edge_device_id: str):
        self.queues_dict[edge_device_id] = queue.Queue(self.size)
        return self.queues_dict[edge_device_id].qsize()

    def delete_message_queue(self, edge_device_id: str):
        if edge_device_id in self.queues_dict:
            self.queues_dict.pop("edge_device_id")
        else:
            logger.error("Could not find edge_device message queue")
            return "Could not find edge_device message queue"
        return True

    def put_message(self, edge_device_id: str, message: dict):
        if edge_device_id in self.queues_dict:
            edge_device_queue = self.queues_dict[edge_device_id]
        else:
            logger.error("Could not find edge_device message queue")
            return "Could not find edge_device message queue"

        message["queued_timestamp"] = time.time()
        try:
            edge_device_queue.put(message, timeout=self.timeout)
        except queue.Full:
            for _ in range(self.items_remove):
                edge_device_queue.get()  # Remove item
            edge_device_queue.put_nowait(message)
        return "Succeed"

    def get_message(self, edge_device_id: str):
        if edge_device_id in self.queues_dict:
            edge_device_queue = self.queues_dict[edge_device_id]
        else:
            logger.error("Could not find edge_device message queue")
            return "Could not find edge_device message queue"

        try:
            message = edge_device_queue.get()
        except edge_device_queue.Empty:
            return None

        queued_timestamp = message.pop("queued_timestamp")
        cutoff_time = time.time() - self.ttl

        while queued_timestamp < cutoff_time:
            edge_device_queue.task_done()
            try:
                message = edge_device_queue.get()
            except edge_device_queue.Empty:
                return None
            queued_timestamp = message.pop("queued_timestamp")

        edge_device_queue.task_done()
        return message

    def get_all_messages(self, edge_device_id: str):
        messages = []
        config_chagange_message = None
        if edge_device_id in self.queues_dict:
            edge_device_queue = self.queues_dict[edge_device_id]
        else:
            logger.error("Could not find edge_device message queue")
            return "Could not find edge_device message queue"

        for _ in range(edge_device_queue.qsize()):
            message = self.get_message(edge_device_id)
            if message["type"] == MessageTypes.configuration_change.value:
                config_chagange_message = message
            else:
                messages.append(message)

        if config_chagange_message is not None:
            messages.append(config_chagange_message)
        return messages


message_queues = MessageQueues(QUEUE_SIZE, QUEUE_PUT_TIMEOUT, QUEUE_TTL, QUEUE_NUMBER_OF_ITEMS_TO_REMOVE_WHEN_FULL)
