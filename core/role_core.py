from sqlalchemy.orm import Session

from app import logger
from db.sql.utils import create_record, delete_record_by_id, get_record_by_id, get_record_by_name, get_records
from models import RoleBase
from schemas import RoleSchema


def get_all_roles(db: Session, skip: int = 0, limit: int = 100):
    roles = get_records(db, skip, limit, RoleSchema)
    if roles is None:
        logger.error("error, roles not found")
        return "error, roles not found"
    return roles


def get_role(db: Session, role_id: int = 0, role_name: str = ""):
    role = None
    if role_id:
        role = get_record_by_id(db, role_id, RoleSchema)
    elif role_name:
        role = get_record_by_name(db, role_name, RoleSchema)

    return role


def new_role(db: Session, role: RoleBase):
    role_schema = RoleSchema(**role.dict(exclude_unset=True))
    role = get_record_by_name(db, role_schema.name, RoleSchema)
    if role is None:
        role_id = create_record(db, role_schema)
        if role_id == 0:
            logger.error("error, can't add role")
            return "error, can't add role"
        return role_id
    else:
        logger.error("error, role name already exists")
        return "error, role name already exists"


def delete_role(db: Session, role_id: int = 0):
    result = delete_record_by_id(db, role_id, RoleSchema)
    if result is None:
        logger.error(f"error, role_id: {role_id} don't exists")
        return f"error, role_id: {role_id} don't exists"
    return result
