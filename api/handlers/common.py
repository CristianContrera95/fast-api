from enum import Enum
from typing import Optional

from fastapi import HTTPException

from core.utils.query_params import SortOrder

SORT_SEPARATOR_CHAR = ":"


def cast_sort_parameters(raw_parameter):
    if raw_parameter is None:
        return None, None

    if len(raw_parameter.split(SORT_SEPARATOR_CHAR)) != 2:
        raise HTTPException(status_code=400, detail="Invalid sort parameter")

    tokens = raw_parameter.split(SORT_SEPARATOR_CHAR)
    try:
        return tokens[0], SortOrder(tokens[1])
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid sort parameter")


class CommonQueryParams:
    def __init__(self, skip: Optional[int] = None, limit: Optional[int] = None, sort: Optional[str] = None):
        self.skip = skip
        self.limit = limit
        self.sort_by, self.sort_order = cast_sort_parameters(sort)
