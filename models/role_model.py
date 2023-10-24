from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str


class RoleModel(RoleBase):
    class Config:
        extra = "allow"
        orm_mode = True

    id = int
