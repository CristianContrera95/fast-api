from typing import Optional

from pydantic import BaseModel


class CloudServiceBase(BaseModel):
    organization_id = int
    cloud_name = str
    resource_name = str
    type = str
    url_endpoint: Optional[str] = None


class CloudService(CloudServiceBase):
    class Config:
        extra = "allow"
        orm_mode = True

    id = int


class CloudCredentialBase(BaseModel):
    cloud_service_id = int
    key = str
    value = str


class CloudCredential(CloudCredentialBase):
    class Config:
        extra = "allow"
        orm_mode = True

    id = int
