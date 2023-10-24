from datetime import datetime, timedelta
from enum import Enum

from azure.storage.blob import AccountSasPermissions, ResourceTypes, generate_account_sas
from sqlalchemy.orm import Session

from core.exceptions.cloud_service_exceptions import CloudCredentialsException
from core.exceptions.entity_not_found_exceptions import CloudServiceNotFoundException
from db.sql.cloud_service_sql import get_cloud_credential_by_key, get_cloud_service_by_organization_id
from models.file_storage_type import FileStorageType

CLIENT_TOKEN_DURATION_IN_HOURS = 1


class ContainerType(str, Enum):
    WORKER_CONTAINER = "CONTAINER_WORKER_NAME"
    ALERT_CONTAINER = "CONTAINER_ALERT_NAME"


def get_temp_token(
    db: Session,
    current_account,
    expiration=datetime.utcnow() + timedelta(hours=CLIENT_TOKEN_DURATION_IN_HOURS),
    container_name=ContainerType.WORKER_CONTAINER,
):
    cloud_service = get_cloud_service_by_organization_id(db, current_account.organization_id)

    if cloud_service is None:
        raise CloudServiceNotFoundException()

    if cloud_service.cloud_name == FileStorageType.Azure:
        return __get_azure_temp_token(db, cloud_service, container_name, expiration)
    else:
        raise Exception("Not implemented " + cloud_service.cloud_name)


def __get_azure_temp_token(db, cloud_service, container_name, expiration):
    try:
        storage_account_name = (
            get_cloud_credential_by_key(db, cloud_service.id, "AZURE_KEY_STORAGE_ACCOUNT_NAME")
            or cloud_service.resource_name
        )
        storage_account_key = get_cloud_credential_by_key(db, cloud_service.id, "AZURE_KEY_STORAGE_ACCOUNT_KEY")
        container_name = get_cloud_credential_by_key(db, cloud_service.id, container_name.value)
    except Exception as e:
        raise CloudCredentialsException(f"Error in find name or key to Azure: {str(e)}")

    if storage_account_name is None or storage_account_key is None:
        raise CloudCredentialsException("Storage name or key not found in credentials to Azure")

    try:
        sas_token = generate_account_sas(
            account_name=storage_account_name.value,
            account_key=storage_account_key.value,
            resource_types=ResourceTypes(object=True, service=True, container=True),
            permission=AccountSasPermissions(read=True, write=True, list=True),
            expiry=expiration,
        )

        return sas_token, storage_account_name.value, container_name.value, cloud_service.cloud_name

    except Exception as e:
        raise CloudCredentialsException(f"Error in name or key credentials to Azure: {str(e)}")
