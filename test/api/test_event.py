import time
from datetime import datetime
from test.api.auth_helper import login

from bson import ObjectId
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.mongodb import mongo_class
from db.sql.edge_device_sql import get_edge_device_by_id

edge_device_id1 = "5fa14853a49b281e76783781"
edge_device_id2 = "5fa16bfba49b281e7678378e"


def parse_date_string(date_time_str):
    return datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S+00:00")


def get_event_from_db(mongo_db, event_id):
    return mongo_db.mydb["events"].find_one({"_id": ObjectId(event_id)})


def start_alert_event_body(edge_device_id=edge_device_id1, behavior="Single Hand"):
    return {
        "edge_device_uid": edge_device_id,
        "use_case": "driver_safety",
        "name": "jetson-dev",
        "type": "start_alert",
        "priority": "low",
        "behavior": behavior,
        "timestamp": "2020-10-28T18:22:45+00:00",
        "truck_id": 45,
    }


def keep_alive_event_body(edge_device_id=edge_device_id1):
    return {
        "edge_device_uid": edge_device_id,
        "use_case": "driver_safety",
        "name": "jetson-dev",
        "type": "keep_alive",
        "timestamp": "2020-10-28T18:22:45+00:00",
        "truck_id": 45,
        "priority": "low",
    }


def basic_event_body(edge_device_id=edge_device_id1):
    return {
        "edge_device_uid": edge_device_id,
        "use_case": "driver_safety",
        "name": "jetson-dev",
        "type": "event_basic",
        "timestamp": "2020-10-31T18:22:45+00:00",
        "truck_id": 45,
        "priority": "low",
    }


def send_frames_event_body(edge_device_id=edge_device_id1, frame=""):
    return {
        "edge_device_uid": edge_device_id,
        "use_case": "driver_safety",
        "name": "jetson-dev",
        "type": "send_frames",
        "timestamp": "2020-10-28T18:22:45+00:00",
        "truck_id": 45,
        "priority": "low",
        "frame": frame,
    }


def end_alert_body(edge_device_id=edge_device_id1, end_time=None):
    return {
        "edge_device_uid": edge_device_id,
        "use_case": "driver_safety",
        "name": "jetson-dev",
        "type": "end_alert",
        "timestamp": end_time,
        "truck_id": 45,
        "priority": "low",
    }


def get_headers(edge_device_id=edge_device_id1, token=None):
    headers = {"Host": "localhost"}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["X-Client-ID"] = edge_device_id
        headers["X-Client-Secret"] = "supersecretshh"
    return headers


class TestEvent:
    device_settings_example = {
        "settings": {
            "API_SEND_FRAME_SKIP_COUNT": 1,
            "API_SEND_FRAME_RESOLUTION": [352, 240],
            "KEEP_ALIVE_TIME": 5,
            "LAST_FRAME_PATH": "last_frame.jpg",
            "LAST_FRAME_STATUS_PATH": "last_frame_status.csv",
            "LAST_ALERT_STATUS_PATH": "last_alert_status.csv",
            "QUEUE_SIZE": 512,
            "QUEUE_PUT_TIMEOUT": 10,
            "QUEUE_NUMBER_OF_ITEMS_TO_REMOVE_WHEN_FULL": 1,
            "SAFE_SEND_FRAME_TIME_PERIOD": 10,
            "GET_FPS": 15,
            "RTSP_END_POINT": "rtsp://172.16.1.22:8000/out.h264",
            "TRT_MODEL_PATH": "artifacts/TensorRT_model.pb",
            "VIDEO_PATH": "artifacts/test1.mp4",
            "CLASS_LABELS": ["down", "mouth", "safe", "tamper", "up"],
            "IMAGE_SIZE": [224, 224],
        }
    }

    def test_basic_event(self, client: TestClient, mongo_db: mongo_class) -> None:
        # Arrange
        body = basic_event_body(edge_device_id1)
        # Act
        response = client.post("/events/", json=body, headers=get_headers())
        content = response.json()

        # Assert
        assert response.status_code == 200
        assert "event" in content.keys()
        event = get_event_from_db(mongo_db, content["event"])

        assert event["event"]["type"] == "event_basic"
        assert event["event"]["priority"] == "low"
        assert event["origin"]["edge_device_id"] == edge_device_id1
        assert event["origin"]["truck_id"] == 45

    def test_start_alert_should_create_event(self, client: TestClient, mongo_db: mongo_class) -> None:
        # Arrange
        body = start_alert_event_body(edge_device_id=edge_device_id1)

        # Act
        response = client.post("/events/", json=body, headers=get_headers())
        content = response.json()

        # Assert
        assert response.status_code == 200
        assert "event" in content.keys()
        event = get_event_from_db(mongo_db, content["event"])

        # Assert on record data.
        assert event["event"]["type"] == "alert"
        assert event["event"]["priority"] == "low"
        assert event["origin"]["edge_device_id"] == edge_device_id1
        assert event["origin"]["truck_id"] == 45
        assert event["payload"]["event_start"] == parse_date_string("2020-10-28T18:22:45+00:00")
        assert event["payload"]["event_end"] is None
        assert event["payload"]["status"] == "ongoing"
        assert event["payload"]["behavior"] == "Single Hand"
        assert len(event["frames"]) == 0

    def test_start_alert_should_close_previous_alerts_of_device(
        self, client: TestClient, mongo_db: mongo_class
    ) -> None:
        # Arrange
        body1 = start_alert_event_body()
        body2 = start_alert_event_body()
        body2["behavior"] = "Eating/Drinking"

        # Act
        response1 = client.post("/events/", json=body1, headers=get_headers())
        response2 = client.post("/events/", json=body2, headers=get_headers())
        alert1 = get_event_from_db(mongo_db, response1.json()["event"])
        alert2 = get_event_from_db(mongo_db, response2.json()["event"])

        # Assert on record data.
        assert alert1["payload"]["event_end"] == parse_date_string(body1["timestamp"])
        assert alert2["payload"]["event_end"] is None

        assert alert1["payload"]["status"] == "ended"
        assert alert2["payload"]["status"] == "ongoing"

    def test_send_frames_should_attach_to_active_alert(self, client: TestClient, mongo_db: mongo_class) -> None:
        # Arrange - Alerts from different devices
        alert1_id = self.send_new_event(client, start_alert_event_body(edge_device_id1), edge_device_id1)
        alert2_id = self.send_new_event(client, start_alert_event_body(edge_device_id2), edge_device_id2)

        body = send_frames_event_body(edge_device_id1, "UHl0aG9uIGlzIGZ1bg==")

        # Act - Frame for edge device 1's active alert
        response = client.post("/events/", json=body, headers=get_headers())
        alert1 = get_event_from_db(mongo_db, alert1_id)
        alert2 = get_event_from_db(mongo_db, alert2_id)
        content = response.json()["event"]

        assert response.status_code == 200
        assert len(content["frames"]) == 1

        assert len(alert1["frames"]) == 1
        assert len(alert2["frames"]) == 0

    def test_end_alert(self, client: TestClient, mongo_db: mongo_class):
        # Arrange - Alerts from different devices
        alert1_id = self.send_new_event(client, start_alert_event_body(edge_device_id1), edge_device_id1)
        alert2_id = self.send_new_event(client, start_alert_event_body(edge_device_id2), edge_device_id2)
        end_time = "2020-10-15T18:22:45+00:00"
        body = end_alert_body(edge_device_id1, end_time)

        # Act - End active alert for edge device 1
        client.post("/events/", json=body, headers=get_headers())
        alert1 = get_event_from_db(mongo_db, alert1_id)
        alert2 = get_event_from_db(mongo_db, alert2_id)

        # Assert on record data.
        assert alert1["payload"]["event_end"] == parse_date_string(end_time)
        assert alert2["payload"]["event_end"] is None

        assert alert1["payload"]["status"] == "ended"
        assert alert2["payload"]["status"] == "ongoing"

    def test_send_multiple_frames(self, client: TestClient, mongo_db: mongo_class):
        # Arrange - Alerts from different devices
        alert_id = self.send_new_event(client, start_alert_event_body(edge_device_id1), edge_device_id1)
        timestamp = parse_date_string("2020-10-28T18:22:45+00:00")
        frame1 = {"storage": "SOMEBASE64IMAGE1", "position": 1, "timestamp": timestamp}
        frame2 = {"storage": "SOMEBASE64IMAGE2", "position": 2, "timestamp": timestamp}

        # Act - Frame for edge device 1's active alert
        client.post("/events/", json=send_frames_event_body(edge_device_id1, frame1["storage"]), headers=get_headers())
        response = client.post(
            "/events/", json=send_frames_event_body(edge_device_id1, frame2["storage"]), headers=get_headers()
        )
        del frame1["storage"]
        del frame2["storage"]

        alert = get_event_from_db(mongo_db, alert_id)
        content = response.json()["event"]

        # Assert - Two frames for alert
        assert response.status_code == 200
        assert len(content["frames"]) == 2

        frames_list = alert["frames"]
        for f in frames_list:
            del f["storage"]

        assert len(frames_list) == 2
        assert frame1 in frames_list
        assert frame2 in frames_list

    def test_send_keepalive_no_message(self, client: TestClient) -> None:
        # Arrange - Add status to edge device 1's queue
        client.post(f"/edge_device/{edge_device_id1}/send_status", headers=get_headers())
        body = keep_alive_event_body(edge_device_id2)

        # Act - Send Keep Alive from edge device 2
        headers = get_headers(edge_device_id2)
        response = client.post("/events/", json=body, headers=headers)
        messages = response.json()["event"]

        # Assert - Empty list of messages
        assert response.status_code == 200
        assert len(messages) == 0

    def test_send_keepalive_status_message(self, client: TestClient) -> None:
        # Arrange - Add send_status message to edge device 1's queue
        token = login(client)
        headers = get_headers(token=token)
        client.post(f"/edge_device/{edge_device_id1}/send_status", headers=headers)

        # Act - Send Keep Alive from edge device 1
        response = client.post(
            "/events/", json=keep_alive_event_body(edge_device_id1), headers=get_headers(edge_device_id1)
        )
        messages = response.json()["event"]

        # Assert - One message for edge device 1
        assert response.status_code == 200
        assert len(messages) == 1
        assert messages[0]["type"] == "send_status"

    def test_send_keepalive_change_settings_message(self, client: TestClient) -> None:
        # Arrange - Add send_status message to edge device 1's queue
        token = login(client)
        headers = get_headers(token=token)
        client.put(f"/edge_device/{edge_device_id1}", json=TestEvent.device_settings_example, headers=headers)

        # Act - Send Keep Alive from edge device 1
        response = client.post(
            "/events/", json=keep_alive_event_body(edge_device_id1), headers=get_headers(edge_device_id1)
        )
        messages = response.json()["event"]

        # Assert - One message for edge device 1
        assert response.status_code == 200
        assert len(messages) == 1
        assert messages[0]["type"] == "configuration_change"
        assert messages[0]["new_config"] == TestEvent.device_settings_example

    def test_events_update_last_interaction(
        self, sql_db: Session, client: TestClient
    ):  # WARNING  - TAKES A COUPLE OF SECONDS
        # Arrange - Get previous interactions
        prev_int1 = get_edge_device_by_id(sql_db, edge_device_id1).last_interaction
        prev_int2 = get_edge_device_by_id(sql_db, edge_device_id2).last_interaction
        time.sleep(1)
        # Act - Post all different types of events
        # Keep Alive
        client.post("/events/", json=keep_alive_event_body(edge_device_id1), headers=get_headers(edge_device_id1))
        last_int1_1 = get_edge_device_by_id(sql_db, edge_device_id1).last_interaction
        time.sleep(1)
        # Basic Event
        client.post("/events/", json=basic_event_body(edge_device_id1), headers=get_headers(edge_device_id1))
        last_int1_2 = get_edge_device_by_id(sql_db, edge_device_id1).last_interaction
        time.sleep(1)

        # Start Alert
        client.post("/events/", json=start_alert_event_body(edge_device_id1), headers=get_headers(edge_device_id1))
        last_int1_3 = get_edge_device_by_id(sql_db, edge_device_id1).last_interaction
        time.sleep(1)

        # Add frame alert
        client.post("/events/", json=send_frames_event_body(edge_device_id1), headers=get_headers(edge_device_id1))
        last_int1_4 = get_edge_device_by_id(sql_db, edge_device_id1).last_interaction
        time.sleep(1)

        # End Alert
        client.post(
            "/events/",
            json=end_alert_body(edge_device_id1, "2020-10-15T18:22:45+00:00"),
            headers=get_headers(edge_device_id1),
        )
        last_int1_5 = get_edge_device_by_id(sql_db, edge_device_id1).last_interaction

        last_int2 = get_edge_device_by_id(sql_db, edge_device_id2).last_interaction

        assert prev_int1 < last_int1_1 < last_int1_2 < last_int1_3 < last_int1_4 < last_int1_5
        assert prev_int2 == last_int2

        """Different edge devices are sending approximately the same payload,
         with same timestamp and truck _id, among other attributes.
         This decision was made in order to keep simplicity, and it's not relevant either."""

    def send_new_event(self, test_client, body, edge_device_id) -> str:
        body["edge_device_uid"] = edge_device_id
        headers = get_headers(edge_device_id)
        response = test_client.post("/events/", json=body, headers=headers)
        return response.json()["event"]
