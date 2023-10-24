from typing import Optional

from pydantic import BaseModel


class OrganizationBase(BaseModel):
    company_id: Optional[int] = None
    name = str
    description: Optional[str] = None
    location: Optional[str] = None


class Organization(OrganizationBase):
    class Config:
        extra = "allow"
        orm_mode = True

    id = int
