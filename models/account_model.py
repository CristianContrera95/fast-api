from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class AccountBase(BaseModel):
    role_id = int
    organization_id: Optional[int] = None
    username = str
    email = EmailStr
    job_title: Optional[str] = None
    last_update: Optional[datetime] = datetime.now()


class AccountCreateUpdate(AccountBase):
    password = str


class Account(AccountBase):
    class Config:
        extra = "allow"
        orm_mode = True

    id = str
