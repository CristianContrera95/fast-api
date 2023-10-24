from schemas import CloudCredentialSchema, CloudServiceSchema


def get_cloud_service_by_resource_name(db, resource_name):
    return db.query(CloudServiceSchema).filter_by(resource_name=resource_name).first()


def get_cloud_service_by_type(db, type):
    return db.query(CloudServiceSchema).filter_by(type=type).first()


def get_cloud_service_by_organization_id(db, organization_id):
    return db.query(CloudServiceSchema).filter_by(organization_id=organization_id).first()


def get_cloud_credentials(db, cloud_service_id, skip, limit):
    return (
        db.query(CloudCredentialSchema)
        .order_by(CloudCredentialSchema.id.desc())
        .filter_by(cloud_service_id=cloud_service_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_cloud_credential_by_key(db, cloud_service_id, key):
    return db.query(CloudCredentialSchema).filter_by(cloud_service_id=cloud_service_id).filter_by(key=key).first()
