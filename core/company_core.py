from sqlalchemy.orm import Session

from app import logger
from db.sql.utils import create_record, delete_record_by_id, get_record_by_id, get_record_by_name, get_records
from models import Company
from schemas import CompanySchema


def get_all_companies(db: Session, skip: int = 0, limit: int = 100):
    companies = get_records(db, skip, limit, CompanySchema)
    if companies is None:
        logger.error("error, companies not found")
        return "error, companies not found"
    return companies


def get_company(db: Session, company_id: int = 0, company_name: str = ""):
    company = None
    if company_id:
        company = get_record_by_id(db, company_id, CompanySchema)
    elif company_name:
        company = get_record_by_name(db, company_name, CompanySchema)

    return company


def new_company(db: Session, company: Company):
    company_schema = CompanySchema(**company.dict(exclude_unset=True))
    print(company.dict(exclude_unset=True))
    company = get_record_by_name(db, company_schema.name, CompanySchema)
    if company is None:
        company_id = create_record(db, company_schema)
        if company_id == 0:
            logger.error("error, can't add company")
            return "error, can't add company"
        return company_id
    else:
        logger.error("error, company name already exists")
        return "error, company name already exists"


def delete_company(db: Session, company_id: int = 0):
    result = delete_record_by_id(db, company_id, CompanySchema)
    if result is None:
        logger.error(f"error, company_id: {company_id} don't exists")
        return f"error, company_id: {company_id} don't exists"
    return result
