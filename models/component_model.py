from enum import Enum

from pydantic import BaseModel


class ComponentType(
    str, Enum
):  # TODO: This names may need adjustments, since pie_chart is not generic, it is for behavior
    pie_chart = "pie_chart"
    piled_up_bar_chart = "piled_up_bar_chart"
    hour_band_chart = "hour_band_chart"
    recent_alerts_list = "recent_alerts_list"
    priorities_radial_bar_chart = "priorities_radial_bar_chart"
    key_metrics = "key_metrics"


class ComponentSettings(BaseModel):
    class Config:
        extra = "allow"

    title: str
    description: str


class Component(BaseModel):
    class Config:
        extra = "allow"

    name: str  # obligatory
    type: ComponentType  # obligatory
    default_settings: ComponentSettings  # obligatory
