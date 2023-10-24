from typing import List

from pydantic import BaseModel


class ViewComponent(BaseModel):
    component_id: str
    position: int
    color: str
    size: str

    class Config:
        extra = "allow"


class View(BaseModel):
    class Config:
        extra = "allow"

    name: str  # obligatory
    components: List[ViewComponent]
