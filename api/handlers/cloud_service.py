from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.sqlserverdb import get_db
from core.cloud_services_core import (
    delete_cloud_service,
    get_all_cloud_services,
    get_cloud_service,
    new_cloud_service,
    update_cloud_service,
)
from models import CloudService

router = APIRouter()


@router.get("/")
def get_all_cloud_services_view(db: Session = Depends(get_db), params: Optional[str] = None):
    all_cloud_services = get_all_cloud_services(db)
    if isinstance(all_cloud_services, str):
        return {"error": "cloud_services not found"}
    return {"cloud_services": all_cloud_services}


@router.get("/{cloud_services_id}")
def get_cloud_service_view(cloud_services_id: int, db: Session = Depends(get_db), params: Optional[str] = None):
    cloud_service = get_cloud_service(db, cloud_services_id)
    if isinstance(cloud_service, str):
        return {"error": "cloud_service_id not valid"}
    else:
        return {"cloud_service": cloud_service}


@router.post("/")
def new_cloud_service_view(cloud_service: CloudService, db: Session = Depends(get_db)):
    result = new_cloud_service(db, cloud_service)
    if isinstance(result, str):
        return {"error": result}
    return {"cloud_service_id": result}


@router.put("/{cloud_service_id}")
def update_cloud_service_view(cloud_service_id: int, cloud_service: CloudService, db: Session = Depends(get_db)):
    result = update_cloud_service(db, cloud_service_id, cloud_service)
    if isinstance(result, str):
        return {"error": result}
    return {"cloud_service": result}


@router.delete("/{cloud_service_id}")
def delete_cloud_service_view(cloud_service_id: int, db: Session = Depends(get_db)):
    result = delete_cloud_service(db, cloud_service_id)
    if isinstance(result, str):
        return {"error": result}
    return {"cloud_service": f"deleted {result} rows"}
