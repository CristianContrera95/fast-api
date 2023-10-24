from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.sqlserverdb import get_db
from core.organization_core import (
    delete_organization,
    get_all_organizations,
    get_organization,
    new_organization,
    update_organization,
)
from models import Organization

router = APIRouter()


@router.get("/")
def get_all_organization_view(db: Session = Depends(get_db), params: Optional[str] = None):
    all_organizations = get_all_organizations(db)
    if isinstance(all_organizations, str):
        return {"error": "organizations not found"}
    return {"organizations": all_organizations}


@router.get("/{organization_id}")
def get_organization_view(organization_id: int, db: Session = Depends(get_db), params: Optional[str] = None):
    organization = get_organization(db, organization_id)
    if isinstance(organization, str):
        return {"error": "organization_id not valid"}
    else:
        return {"organization": organization}


@router.post("/")
def new_organization_view(organization: Organization, db: Session = Depends(get_db)):
    result = new_organization(db, organization)
    if isinstance(result, str):
        return {"error": result}
    return {"organization_id": result}


@router.put("/{organization_id}")
def update_organization_view(organization_id: int, organization: Organization, db: Session = Depends(get_db)):
    result = update_organization(db, organization_id, organization)
    if isinstance(result, str):
        return {"error": result}
    return {"organization": result}


@router.delete("/{organization_id}")
def delete_organization_view(organization_id: int, db: Session = Depends(get_db)):
    result = delete_organization(db, organization_id)
    if isinstance(result, str):
        return {"error": result}
    return {"organization": f"deleted {result} rows"}
