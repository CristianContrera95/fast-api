from pydantic import BaseModel


class ViewUsersBase(BaseModel):
    role_id = int
    organization_id = int
    view_id = str


class ViewRole(ViewUsersBase):
    class Config:
        extra = "allow"
        orm_mode = True

    id = int
