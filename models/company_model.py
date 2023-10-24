from typing import Optional

from pydantic import BaseModel


class CompanyBase(BaseModel):
    name = str
    type: Optional[str] = None


class Company(CompanyBase):
    class Config:
        extra = "allow"
        orm_mode = True

    id = int
