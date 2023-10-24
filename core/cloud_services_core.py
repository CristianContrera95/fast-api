from sqlalchemy.orm import Session

from app import logger
from db.sql.cloud_service_sql import (
    get_cloud_credential_by_key,
    get_cloud_credentials,
    get_cloud_service_by_resource_name,
)
from db.sql.utils import create_record, delete_record_by_id, get_record_by_id, get_records, update_record_by_id
from models import CloudCredentialBase, CloudService, CloudServiceBase
from schemas import CloudCredentialSchema, CloudServiceSchema


def get_all_cloud_services(db: Session, skip: int = 0, limit: int = 100):
    cloud_services = get_records(db, skip, limit, CloudServiceSchema)
    if cloud_services is None:
        logger.error("error, cloud_services not found")
        return "error, cloud_services not found"
    return cloud_services


def get_all_cloud_credentials(db: Session, cloud_service_id: int, skip: int = 0, limit: int = 100):
    """all cloud credentials over one cloud service"""
    cloud_credentials = get_cloud_credentials(db, cloud_service_id, skip, limit)
    if cloud_credentials is None:
        logger.error("error, cloud_services not found")
        return "error, cloud_services not found"
    return cloud_credentials


def get_cloud_service(db: Session, cloud_service_id: int = 0, cloud_service_resource_name: str = ""):
    cloud_service = None
    if cloud_service_id:
        cloud_service = get_record_by_id(db, cloud_service_id, CloudServiceSchema)
    elif cloud_service_resource_name:
        cloud_service = get_cloud_service_by_resource_name(db, cloud_service_resource_name)

    if cloud_service is None:
        logger.error("error, cloud_service not found")
        return "error, cloud_service not found"
    return cloud_service


def get_cloud_credential(
    db: Session,
    cloud_credential_id: int = 0,
    cloud_credential_key: str = "",
    cloud_service_id: int = 0,
):
    cloud_credential = None
    if cloud_credential_id:
        cloud_credential = get_record_by_id(db, cloud_credential_id, CloudCredentialSchema)
    elif cloud_credential_key:
        cloud_credential = get_cloud_credential_by_key(db, cloud_service_id, cloud_credential_key)

    if cloud_credential is None:
        logger.error("error, cloud_credential not found")
        return "error, cloud_credential not found"
    return cloud_credential


def __check_unique(
    db: Session,
    cloud_service: CloudServiceSchema = None,
    cloud_credential: CloudCredentialSchema = None,
    cloud_service_id: int = 0,
):
    result = False
    if cloud_service is not None:
        result = get_cloud_service_by_resource_name(db, cloud_service.resource_name)
    elif cloud_credential:
        result = get_cloud_credential_by_key(db, cloud_service_id, cloud_credential.key)

    return not bool(result)


def new_cloud_service(db: Session, cloud_service: CloudService):
    cloud_service_schema = CloudServiceSchema(**cloud_service.dict(exclude_unset=True))
    if __check_unique(db, cloud_service=cloud_service_schema):
        cloud_service_id = create_record(db, cloud_service_schema)
        if cloud_service_id == 0:
            logger.error("error, can't add cloud_service")
            return "error, can't add cloud_service"
        return cloud_service_id
    else:
        logger.error("error, cloud_service's name already exists")
        return "error, cloud_service's name already exists"


def new_cloud_credential(db: Session, cloud_credential: CloudService):
    cloud_credential_schema = CloudCredentialSchema(**cloud_credential.dict(exclude_unset=True))
    if __check_unique(
        db, cloud_credential=cloud_credential_schema, cloud_service_id=cloud_credential_schema.cloud_service_id
    ):
        cloud_credential_id = create_record(db, cloud_credential_schema)
        if cloud_credential_id == 0:
            logger.error("error, can't add cloud_credential")
            return "error, can't add cloud_credential"
        return cloud_credential_id
    else:
        error_message = "error, cloud_credential's key already exists in cloud_service id: " + str(
            cloud_credential_schema.cloud_service_id
        )
        logger.error(error_message)
        return error_message


def update_cloud_service(db: Session, cloud_service_id: int, cloud_service: CloudServiceBase):
    updated_cloud_service = update_record_by_id(
        db, cloud_service_id, cloud_service.dict(exclude_unset=True), CloudServiceSchema
    )
    if updated_cloud_service is None:
        logger.error(f"error, cloud_service {cloud_service_id} don't exists")
        return f"error, cloud_service {cloud_service_id} don't exists"
    return updated_cloud_service


def update_cloud_credential(db: Session, cloud_credential_id: int, cloud_credential: CloudCredentialBase):
    updated_cloud_credential = update_record_by_id(
        db, cloud_credential_id, cloud_credential.dict(exclude_unset=True), CloudCredentialSchema
    )
    if updated_cloud_credential is None:
        logger.error(f"error, cloud_service {cloud_credential_id} don't exists")
        return f"error, cloud_service {cloud_credential_id} don't exists"
    return updated_cloud_credential


def delete_cloud_service(db: Session, cloud_service_id: int):
    result = delete_record_by_id(db, cloud_service_id, CloudServiceSchema)
    if result is None:
        logger.error(f"error, cloud_service_id: {cloud_service_id} don't exists")
        return f"error, cloud_service_id: {cloud_service_id} don't exists"
    return result


def delete_cloud_credential(db: Session, cloud_credential_id: int):
    result = delete_record_by_id(db, cloud_credential_id, CloudCredentialSchema)
    if result is None:
        logger.error(f"error, cloud_credential_id: {cloud_credential_id} don't exists")
        return f"error, cloud_credential_id: {cloud_credential_id} don't exists"
    return result
