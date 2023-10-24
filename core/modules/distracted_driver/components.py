from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy.orm import Session

from core.modules.distracted_driver.alert_behaviors import AlertBehaviors
from core.modules.distracted_driver.alert_model_out import AlertModelOut
from core.utils.query_params import SortOrder
from db.mongodb import edge_device_mongo, event_mongo
from db.sql import worker_sql
from models.component_model import ComponentType
from models.event_model import EventType
from models.use_case_model import UseCaseModel


class TimeUnits(str, Enum):
    """ Represents time units in which data can be grouped to be represented in components """

    year = "year"
    month = "month"
    day = "dayOfMonth"
    hour = "hour"
    minute = "minute"

    @classmethod
    def ordered_list(cls):
        return [TimeUnits.year, TimeUnits.month, TimeUnits.day, TimeUnits.hour, TimeUnits.minute]

    @classmethod
    def add_to_date(cls, date: datetime, unit, delta):
        if unit == TimeUnits.year:
            return date.replace(year=date.year + delta)
        if unit == TimeUnits.month:
            return date.replace(year=(date.month + delta / 12), month=(date.month + delta % 12) + 1)
        if unit == TimeUnits.day:
            return date + timedelta(days=delta)
        if unit == TimeUnits.hour:
            return date + timedelta(hours=delta)
        if unit == TimeUnits.minute:
            return date + timedelta(minutes=delta)

    @classmethod
    def min_date_interval(cls, date, unit, delta, min_date):
        trimmed = min_date
        new_date = TimeUnits.add_to_date(trimmed, unit=unit, delta=-delta)
        while new_date > date:
            new_date = TimeUnits.add_to_date(trimmed, unit=unit, delta=-delta)
            trimmed = new_date
        return trimmed


def generate_driver_safety_component(db: Session, component_data, filters=None):
    if component_data["type"] == ComponentType.pie_chart:
        return generate_pie_chart(component_data, filters)
    if component_data["type"] == ComponentType.piled_up_bar_chart:
        return generate_piled_up_bar_chart(component_data, filters)
    if component_data["type"] == ComponentType.hour_band_chart:
        return generate_hour_band_chart(component_data)
    if component_data["type"] == ComponentType.recent_alerts_list:
        return generate_latest_alerts_list(component_data)
    if component_data["type"] == ComponentType.priorities_radial_bar_chart:
        return generate_priority_radial_bar_chart(component_data, filters)
    if component_data["type"] == ComponentType.key_metrics:
        return generate_key_metrics(db)


# PIE CHART


def generate_pie_chart(component_data, filters=None):
    mongo_filters = {"category": "driver_safety"}  # Always impose use case as fixed filter
    if filters:
        mongo_filters.update({"timestamp": {"$gte": datetime.now() - timedelta(days=filters["days"])}})

    # applied_filters = add_filters(mongo_filters,
    #                               component_data)  # Add default filters from component data retrieved from mongo

    counts = event_mongo.group_count(
        "$payload.behavior", mongo_filters, extra_settings=[{"$unwind": "$payload.behavior"}]
    )  # Group counts by behavior, applying filters

    # Return data with format specified in docs
    data = []
    for count in counts:
        data.append({"x": count["_id"], "y": count["count"]})
    data = list(sorted(data, key=lambda x: x["y"], reverse=True))
    return {"data": data, "applied_filters": mongo_filters}


# BAR CHART


def generate_piled_up_bar_chart(component_data, filters=None):
    # Group counts of events in time intervals, and by category
    counts, applied_filters = calculate_events_by_interval(component_data)

    result = {
        "data": [],
        "applied_filters": {**applied_filters, "time_interval": component_data["default_filters"]["time_interval"]},
    }
    if len(counts) == 0:
        return result

    # Arrange list of groups returned by mongo in a dictionary
    time_slots = {}
    for count in counts:
        add_datetime_entry(time_slots, count)

    # Complete missing intervals (intervals with 0, not returned by mongo)
    complete_missing_intervals(time_slots, component_data)

    # Sort dates and format
    sorted_dates = sorted(time_slots)
    x_bins = list(map(lambda ts: {"x": ts, "y": time_slots[ts]}, sorted_dates))

    result["data"] = x_bins

    return result
    # return {"data": x_bins,
    #         "applied_filters": {**applied_filters, "time_interval": component_data["default_filters"]["time_interval"]}}


# HOUR BAND COUNTS


def generate_hour_band_chart(component_data):
    mongo_filters = {"category": "driver_safety"}  # Always impose use case as fixed filter
    applied_filters = add_filters(
        mongo_filters, component_data
    )  # Add default filters from component data retrieved from mongo
    group_by = {"$hour": "$timestamp"}

    bucket_boundaries = component_data["default_filters"]["hour_bands"]
    counts = event_mongo.bucket_count(group_by, bucket_boundaries, mongo_filters)
    formatted_counts = format_hour_bands(counts, bucket_boundaries, component_data["default_filters"]["band_tags"])

    return {
        "data": formatted_counts,
        "applied_filters": {
            **applied_filters,
            "hour_bands": component_data["default_filters"]["hour_bands"],
            "band_tags": component_data["default_filters"]["band_tags"],
        },
    }


# ALERT LISTS


def generate_latest_alerts_list(component_data):
    limit = component_data["default_filters"]["limit"]
    db_events = event_mongo.get_all_events(
        filters={"event.type": "alert"}, limit=limit, sort_fields=[("timestamp", -1)]
    )
    out_models = [
        AlertModelOut(**e, **e["payload"], **e["origin"], use_case=e["category"], **e["event"]) for e in db_events
    ]

    return {"data": out_models}


# ALERTS BY PRIORITY


def generate_priority_radial_bar_chart(component_data, filters=None):
    mongo_filters = {"category": "driver_safety"}  # Always impose use case as fixed filter
    # applied_filters = add_filters(mongo_filters,
    #                               component_data)  # Add default filters from component data retrieved from mongo
    if filters:
        mongo_filters.update({"timestamp": {"$gte": datetime.now() - timedelta(days=filters["days"])}})

    counts = event_mongo.group_count("$event.priority", mongo_filters)  # Group counts by priority, applying filters
    # Return data with format specified in docs
    data = []
    for count in counts:
        data.append({"x": count["_id"], "y": count["count"]})
    return {"data": data, "applied_filters": mongo_filters}


# KEY METRICS


def generate_key_metrics(db: Session):
    total_alerts_count = event_mongo.count({"category": UseCaseModel.driver_safety, "event.type": EventType.alert})
    last_high_priority_alert = event_mongo.get_all_events(
        {"category": UseCaseModel.driver_safety, "event.type": EventType.alert, "payload.priority": "high"},
        0,
        1,
        [("timestamp", SortOrder.desc)],
    )

    if not last_high_priority_alert:
        # TODO:  Trying to guess system uptime.
        first_event_ever = event_mongo.get_all_events(offset=0, limit=1, sort_fields=[("timestamp", SortOrder.asc)])
        print(first_event_ever)
        first_event_ever = 0 if not first_event_ever else first_event_ever[0]
        days_since_last_high_alert = (datetime.now() - first_event_ever["timestamp"]).days
    else:
        last_high_priority_alert = last_high_priority_alert[0]
        days_since_last_high_alert = (datetime.now() - last_high_priority_alert["timestamp"]).days

    total_trucks = edge_device_mongo.count({})

    total_processed_videos = worker_sql.get_worker_finished_jobs_count(db)

    key_metrics = {
        "total_alerts": total_alerts_count,
        "days_without_high_priority_alerts": days_since_last_high_alert,
        "total_trucks": total_trucks,
        "total_analyzed_videos": total_processed_videos,
    }
    return {"data": key_metrics}


def format_hour_bands(hour_band_counts, bucket_boundaries, bucket_tags):
    formatted_counts = []
    hour_band_counts.sort(key=lambda x: x["_id"])
    hb_bucket, hb_count = 0, 0

    while hb_bucket < len(bucket_boundaries) and hb_count < len(hour_band_counts):
        current_count = hour_band_counts[hb_count]
        formatted_count = {
            "tag": bucket_tags[hb_bucket],
            "from": bucket_boundaries[hb_bucket],
            "to": bucket_boundaries[(hb_bucket + 1) % len(bucket_boundaries)],
            "count": 0,
        }
        if current_count["_id"] == bucket_boundaries[hb_bucket]:
            formatted_count["count"] = current_count["count"]
            hb_count += 1
        formatted_counts.append(formatted_count)
        hb_bucket += 1

    return formatted_counts


def add_single_filter(filters, mongo_filters, applied_filters={}):
    """Adds to mongo_filters object the translation of objects from filters"""
    key = mongo_filters[0]
    if key == "init_date":
        filters.setdefault("timestamp", {})
        abs_date = datetime.now() + timedelta(seconds=mongo_filters[1])
        filters["timestamp"]["$gte"] = abs_date
        applied_filters[key] = abs_date
    if key == "end_date":
        abs_date = datetime.now() + timedelta(seconds=mongo_filters[1])
        filters["timestamp"]["$lt"] = abs_date
        applied_filters[key] = abs_date


def add_filters(filters, component):
    added_filters = {}
    for f in component["default_filters"].items():
        add_single_filter(filters, f, added_filters)
    return added_filters


def add_datetime_entry(time_slots, count):
    date_units = count["_id"]
    year = date_units[TimeUnits.year]
    month = date_units.get(TimeUnits.month, 1)
    day = date_units.get(TimeUnits.day, 1)
    hour = date_units.get(TimeUnits.hour, 0)
    minute = date_units.get(TimeUnits.minute, 0)

    counts_by_category = dict((cat, 0) for cat in AlertBehaviors.__members__.keys())
    for cat in count["categories"]:
        counts_by_category[cat["category"]] = cat["count"]
    time_slots[datetime(year=year, month=month, day=day, hour=hour, minute=minute)] = {"categories": counts_by_category}


def complete_missing_intervals(time_slots, component_data):
    counts_by_category = dict((cat, 0) for cat in AlertBehaviors.__members__.keys())
    default_filters = component_data["default_filters"]
    unit = default_filters["time_interval"]["unit"]
    size = default_filters["time_interval"]["size"]
    start_time = datetime.now() + timedelta(seconds=default_filters["init_date"])

    # Get the minimum time inside the range that fits in the sequence of grouping dates.
    current_time = TimeUnits.min_date_interval(start_time, unit, size, min(time_slots.keys()))

    min_interval_in_range = current_time
    end_date = datetime.now() + timedelta(seconds=default_filters["end_date"])
    # Add the missing dates in the sequence
    while current_time < end_date:
        if current_time not in time_slots:
            time_slots[current_time] = {"categories": counts_by_category}
        # step, determined by time unit and size
        current_time = TimeUnits.add_to_date(current_time, unit=unit, delta=size)

    # The first time of the grouping can be less than de init_time, adjust.
    if start_time not in time_slots:
        time_slots[start_time] = time_slots[min_interval_in_range]
        del time_slots[min_interval_in_range]


def calculate_events_by_interval(component_data):
    mongo_filters = {"category": "driver_safety"}
    applied_filters = add_filters(mongo_filters, component_data)
    bin_data = component_data["default_filters"]["time_interval"]
    unit = bin_data["unit"]
    size = bin_data.get("size", 1)
    group_by_date = {}
    group_by_category = {}
    units = TimeUnits.ordered_list()

    time_field = "$timestamp"
    for u in units:
        group_by_category[f"{u}"] = f"$_id.{u}"
        if unit == u:
            group_by_date[f"{u}"] = {"$subtract": [{f"${u}": time_field}, {"$mod": [{f"${u}": time_field}, size]}]}
            break
        group_by_date[f"{u}"] = {f"${u}": time_field}

    group_by_date["behavior"] = "$payload.behavior"
    group_by_category_pipe = {
        "$group": {"_id": group_by_category, "categories": {"$push": {"category": "$_id.behavior", "count": "$count"}}}
    }
    counts = event_mongo.group_count(
        group_by_date,
        mongo_filters,
        extra_settings=[{"$unwind": "$payload.behavior"}],
        further_groupings=[group_by_category_pipe],
    )
    return counts, applied_filters
