from sqlalchemy.orm import Session

from app import logger
from db.sql.utils import (
    create_record,
    delete_record_by_id,
    get_record_by_id,
    get_record_by_name,
    get_records,
    update_record_by_id,
)
from models import OrganizationBase
from schemas import OrganizationSchema


def get_all_organizations(db: Session, skip: int = 0, limit: int = 100):
    organizations = get_records(db, skip, limit, OrganizationSchema)
    if organizations is None:
        logger.error("error, organizations not found")
        return "error, organizations not found"
    return organizations


def get_organization(db: Session, organization_id: int = 0, organization_name: str = ""):
    organization = None
    if organization_id:
        organization = get_record_by_id(db, organization_id, OrganizationSchema)
    elif organization_name:
        organization = get_record_by_name(db, organization_name, OrganizationSchema)

    if organization is None:
        logger.error("error, organization not found")
        return "error, organization not found"
    return organization


def __check_unique(db: Session, organization: OrganizationSchema):
    organization = get_record_by_name(db, organization.name, OrganizationSchema)
    if organization:
        return False

    return True


def new_organization(db: Session, organization: OrganizationBase):
    organization_schema = OrganizationSchema(**organization.dict(exclude_unset=True))
    if __check_unique(db, organization_schema):
        organization_id = create_record(db, organization_schema)
        if organization_id == 0:
            logger.error("error, can't add organization")
            return "error, can't add organization"
        return organization_id
    else:
        logger.error("error, organization's name already exists")
        return "error, organization's name already exists"


def update_organization(db: Session, organization_id: int, organization: OrganizationBase):
    updated_organization = update_record_by_id(
        db, organization_id, organization.dict(exclude_unset=True), OrganizationSchema
    )
    if updated_organization is None:
        logger.error(f"error, organization {organization_id} don't exists")
        return f"error, organization {organization_id} don't exists"
    return updated_organization


def delete_organization(db: Session, organization_id: int):
    result = delete_record_by_id(db, organization_id, OrganizationSchema)
    if result is None:
        logger.error(f"error, organization_id: {organization_id} don't exists")
        return f"error, organization_id: {organization_id} don't exists"
    return result
