import os

from app.sqlserverdb import SessionLocal

from ..cloud_services_core import get_cloud_credential, get_cloud_service
from .Storage import Storage

db = SessionLocal()

# STORAGE_FRAMES is the name of Storage-Account on Azure or S3-bucket on AWS
stg_resource = get_cloud_service(db=db, cloud_service_resource_name=os.environ["STORAGE_FRAMES"])

kwargs = None

if stg_resource.cloud_name.lower() == "azure":

    stg_acc_key = get_cloud_credential(
        db=db, cloud_credential_key="AZURE_KEY_STORAGE_ACCOUNT_KEY", cloud_service_id=stg_resource.id
    )
    container_name = get_cloud_credential(
        db=db, cloud_credential_key="CONTAINER_ALERT_NAME", cloud_service_id=stg_resource.id
    )

    kwargs = {
        "AZURE_KEY_STORAGE_ACCOUNT_NAME": stg_resource.resource_name,
        "AZURE_KEY_STORAGE_ACCOUNT_KEY": stg_acc_key.value,
        "CONTAINER_NAME": container_name.value,
    }

elif stg_resource.cloud_name.lower() == "aws":
    pass


event_storage = Storage(stg_resource.cloud_name.lower(), **kwargs)
