from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.sqlserverdb import get_db
from core.cloud_services_core import (
    delete_cloud_credential,
    get_all_cloud_credentials,
    get_cloud_credential,
    new_cloud_credential,
    update_cloud_credential,
)
from models import CloudCredential

router = APIRouter()


@router.get("/")
def get_all_cloud_credentials_view(
    db: Session = Depends(get_db), cloud_service_id: int = 0, params: Optional[str] = None
):
    all_cloud_credentials = get_all_cloud_credentials(db, cloud_service_id)
    if isinstance(all_cloud_credentials, str):
        return {"error": "cloud_credentials not found"}
    return {"cloud_credentials": all_cloud_credentials}


@router.get("/{cloud_credentials_id}")
def get_cloud_credential_view(cloud_credentials_id: int, db: Session = Depends(get_db), params: Optional[str] = None):
    cloud_credential = get_cloud_credential(db, cloud_credentials_id)
    if isinstance(cloud_credential, str):
        return {"error": "cloud_credential_id not valid"}
    else:
        return {"cloud_credential": cloud_credential}


@router.post("/")
def new_cloud_credential_view(cloud_credential: CloudCredential, db: Session = Depends(get_db)):
    result = new_cloud_credential(db, cloud_credential)
    if isinstance(result, str):
        return {"error": result}
    return {"cloud_credential_id": result}


@router.put("/{cloud_credential_id}")
def update_cloud_credential_view(
    cloud_credential_id: int, cloud_credential: CloudCredential, db: Session = Depends(get_db)
):
    result = update_cloud_credential(db, cloud_credential_id, cloud_credential)
    if isinstance(result, str):
        return {"error": result}
    return {"cloud_credential": result}


@router.delete("/{cloud_credential_id}")
def delete_cloud_credential_view(cloud_credential_id: int, db: Session = Depends(get_db)):
    result = delete_cloud_credential(db, cloud_credential_id)
    if isinstance(result, str):
        return {"error": result}
    return {"cloud_credential": f"deleted {result} rows"}
