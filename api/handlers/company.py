from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.sqlserverdb import get_db
from core.company_core import delete_company, get_all_companies, get_company, new_company
from models import Company

router = APIRouter()


@router.get("/")  # , response_model=List[RoleModel]
def get_all_companies_view(db: Session = Depends(get_db), params: Optional[str] = None):
    all_companies = get_all_companies(db)
    return {"companies": all_companies}


@router.get("/{company_id}")
def get_company_view(company_id: int, db: Session = Depends(get_db), params: Optional[str] = None):
    company = get_company(db, company_id)
    if company is None:
        return {"error": f"company_id: {company_id} not valid"}
    return {"company": company}


@router.delete("/{company_id}")
def delete_company_view(company_id: int, db: Session = Depends(get_db)):
    result = delete_company(db, company_id)
    if isinstance(result, str):
        return {"error": result}
    return {"company": f"deleted {result} rows"}


@router.post("/")
def new_company_view(company_model: Company, db: Session = Depends(get_db)):
    result = new_company(db, company_model)
    if isinstance(result, str):
        return {"error": result}
    return {"company_id": result}
