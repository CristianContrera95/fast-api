from schemas.view_associations import ViewAccountAssociationSchema, ViewRoleAssociationSchema


def get_views_by_organization_id(db, organization_id, skip, limit):
    return (
        db.query(ViewRoleAssociationSchema)
        .order_by(ViewRoleAssociationSchema.id.desc())
        .filter_by(organization_id=organization_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_views_by_account_id(db, account_id, skip, limit):
    return (
        db.query(ViewAccountAssociationSchema)
        .order_by(ViewAccountAssociationSchema.id.desc())
        .filter_by(account_id=account_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_views_by_role_id(db, role_id, skip, limit):
    return (
        db.query(ViewRoleAssociationSchema)
        .order_by(ViewRoleAssociationSchema.id.desc())
        .filter_by(role_id=role_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_views_by_role_organization(db, role_id, organization_id, skip, limit):
    return (
        db.query(ViewRoleAssociationSchema)
        .order_by(ViewRoleAssociationSchema.id.desc())
        .filter_by(organization_id=organization_id)
        .filter_by(role_id=role_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
