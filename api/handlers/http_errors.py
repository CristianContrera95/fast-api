import logging
import traceback

from fastapi import HTTPException

from core.exceptions.entity_not_found_exceptions import EntityNotFoundException
from core.exceptions.not_authorized_exceptions import NotAuthorizedException

logger = logging.getLogger(__name__)


def handle_exception(e: Exception):
    traceback.print_exc()
    if issubclass(e.__class__, EntityNotFoundException):
        raise HTTPException(status_code=404, detail=str(e))
    if issubclass(e.__class__, NotAuthorizedException):
        raise HTTPException(status_code=403, detail=str(e))
    raise HTTPException(status_code=500, detail=str(e))
