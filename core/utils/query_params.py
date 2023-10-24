from enum import Enum


class SortOrder(str, Enum):
    asc = ("asc",)
    desc = "desc"


def exclude_none_keys(fields):
    return {k: v for k, v in fields.items() if v is not None}
