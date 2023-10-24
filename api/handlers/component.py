from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.auth import auth
from app.sqlserverdb import get_db
from core import component_core
from models import component_model
from models.account_model import Account
from models.component_model import Component

router = APIRouter()


@router.get("/{component_uid}")  # GET /component
# Permite obtener uno o una lista de los componentes disponibles para el usuario que realiza la petición.
# Response: una lista o un componente disponibles para el usuario con su configuracion.
def get_component(params: Optional[str] = None, current_account: Account = Depends(auth.get_current_account)):
    ########
    # @TODO
    return Component.Config


@router.post("/")
def create_component(
    component: component_model.Component,
    db: Session = Depends(get_db),
    current_account: Account = Depends(auth.get_current_account),
):
    component_id = component_core.new_component(db, component)
    return {"component": component_id}


@router.get("/view/{component_uid}")
def get_component_view(
    component_uid: str, days: Optional[int] = None, db: Session = Depends(get_db), _=Depends(auth.get_current_account)
):
    filters = {"days": days} if days else None
    component_view = component_core.generate_component(db, component_uid, filters)
    return {"component": component_view}
