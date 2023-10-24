import logging

from sqlalchemy.orm import Session

from core.component_core import generate_component
from core.exceptions.entity_not_found_exceptions import EntityNotFoundException, ViewNotFoundException
from core.exceptions.not_authorized_exceptions import NotAuthorizedViewException
from db.mongodb import view_mongo
from db.sql import component_sql, view_sql
from models import Account
from models.view_model import View
from schemas.view_schema import ViewSchema

logger = logging.getLogger(__name__)


def new_view(db: Session, view: View):
    errors = {}
    checked_components = []
    for c in view.components:
        if not component_sql.exists(db, c.component_id):
            logger.error(f"Could not generate component {c.component_id}")
            errors[c.component_id] = "Not Found"
        else:
            checked_components.append(c)

    view.components = checked_components

    view_dict = view.dict(exclude_unset=True)
    created_view_id = view_mongo.new_view(view_dict)
    view_schema = ViewSchema(**{"id": created_view_id, "name": view.name})

    return view_sql.create_view(db, created_view_id, view_schema), errors


def generate_view(db: Session, view_id: str, reader_account: Account):
    view_record = view_sql.get_view_by_id(db, view_id)
    if view_record is None:
        logger.error("Component not found in sql db.")
        raise ViewNotFoundException()

    view_document = view_mongo.get_view(view_id)
    if view_document is None:
        logger.error("Component not found in mongo db.")
        raise ViewNotFoundException()

    __validate_view_permissions(reader_account, view_record)

    generated_view = {"view_id": view_document["_id"], "components": []}
    for c in view_document["components"]:
        try:
            generated_component = generate_component(db, c["component_id"])
            list_entry = __component_entry(c, generated_component)
        except EntityNotFoundException as e:
            list_entry = __generate_error_entry(c, str(e))

        generated_view["components"].append(list_entry)

    return generated_view


def __validate_view_permissions(reader_account: Account, view_record: ViewSchema):
    is_account_allowed_by_role = any(vr.id == reader_account.role_id for vr in view_record.roles_allowed)

    # If not allowed by role, check if it is was assigned permission individually.
    account_allowed = is_account_allowed_by_role or any(
        acc.id == reader_account.id for acc in view_record.single_accounts_allowed
    )

    if not account_allowed:
        error_str = f"Account of id {reader_account.role_id} is not allowed to get view of id {view_record.id}"
        logger.error(error_str)
        raise NotAuthorizedViewException(error_str)


def __component_entry(component_data, generated_component):
    return {
        "component_id": component_data["component_id"],
        "error": False,
        "position": component_data["position"],
        "size": component_data["size"],
        "component": generated_component,
    }


def __generate_error_entry(component_data, error_message):
    return {"component_id": component_data["component_id"], "error": True, "message": error_message}
