from sqlalchemy.orm import Session

from core.exceptions.entity_not_found_exceptions import (
    RoleNotFoundException,
    ViewNotFoundException,
    ViewPermissionNotFoundException,
)
from core.exceptions.not_authorized_exceptions import NotAuthorizedException
from core.role_core import get_role
from db.sql.utils import create_record, delete_record_by_id, get_record_by_id, update_record_by_id
from db.sql.view_permissions_sql import (
    get_views_by_organization_id,
    get_views_by_role_id,
    get_views_by_role_organization,
)
from models import Account, ViewRole
from schemas import RoleSchema
from schemas.view_associations import ViewRoleAssociationSchema
from schemas.view_schema import ViewSchema


def get_view_role_by_id(db: Session, view_role_id):
    view_users = get_record_by_id(db, view_role_id, ViewRoleAssociationSchema)
    if view_users is None:
        raise ViewPermissionNotFoundException()
    return view_users


def get_all_view_permissions_by(
    db: Session, role_id: int = None, organization_id: int = None, skip: int = 0, limit: int = 100
):
    views_users = None
    if (role_id is not None) and (organization_id is not None):
        views_users = get_views_by_role_organization(db, role_id, organization_id, skip, limit)
    elif role_id is not None:
        views_users = get_views_by_role_id(db, role_id, skip, limit)
    elif organization_id is not None:
        views_users = get_views_by_organization_id(db, organization_id, skip, limit)

    if views_users is None:
        raise ViewPermissionNotFoundException("Could not find view-role association.")
    return views_users


def __get_role_and_view(db, role_id, organization_id, view_id):
    view = get_record_by_id(db, view_id, ViewSchema)

    if view is None:
        raise ViewNotFoundException()

    role = get_record_by_id(db, role_id, RoleSchema)

    if role is None:
        raise RoleNotFoundException()

    # organization = get_record_by_id(db, organization_id, OrganizationSchema)
    #
    # if organization is None:
    #     raise OrganizationNotFoundException()

    return role, view


def new_view_role(db: Session, view_role: ViewRole, granter: Account):
    role = get_role(db, granter.role_id)
    authorized = True  # TODO CHECK WH0 CAN GRANT ROLES, POLICY

    if (role is None) or not authorized:
        raise NotAuthorizedException()

    role, view = __get_role_and_view(db, view_role.role_id, view_role.organization_id, view_role.view_id)
    view_users_schema = ViewRoleAssociationSchema(**view_role.dict(exclude_unset=True), role=role, view=view)
    view_users_id = create_record(db, view_users_schema, view.roles_allowed)
    return view_users_id


def update_view_role(db: Session, view_role_id: int, view_users: ViewRole):
    updated_view_users = update_record_by_id(
        db, view_role_id, view_users.dict(exclude_unset=True), ViewRoleAssociationSchema
    )
    if updated_view_users is None:
        raise ViewPermissionNotFoundException(f"view_role id: {view_role_id} doesn't exist")

    return updated_view_users


def delete_view_role(db: Session, view_role_id: int, remover: Account):
    role = get_role(db, role_id=remover.role_id)
    authorized = True  # TODO CHECK WH0 CAN GRANT ROLES, POLICY

    if (role is None) or not authorized:
        raise NotAuthorizedException()

    result = delete_record_by_id(db, view_role_id, ViewRoleAssociationSchema)

    if result is None:
        raise ViewPermissionNotFoundException(f"view_role id: {view_role_id} doesn't exist")
    return result
