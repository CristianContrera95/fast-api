from fastapi import APIRouter

from .auth import auth
from .handlers import (
    account,
    cloud_credential,
    cloud_service,
    company,
    component,
    edge_device,
    events,
    job,
    organization,
    role,
    storage,
    trucks,
    view,
    view_permissions,
    worker,
    worker_credential,
    worker_queue,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="", tags=["token"])
api_router.include_router(role.router, prefix="/role", tags=["role"])
api_router.include_router(account.router, prefix="/account", tags=["account"])
api_router.include_router(company.router, prefix="/company", tags=["company"])
api_router.include_router(organization.router, prefix="/organization", tags=["organization"])
api_router.include_router(cloud_service.router, prefix="/cloud_service", tags=["cloud_service"])
api_router.include_router(cloud_credential.router, prefix="/cloud_credential", tags=["cloud_credential"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(edge_device.router, prefix="/edge_device", tags=["edge_device"])
api_router.include_router(trucks.router, prefix="/trucks", tags=["truck"])
api_router.include_router(component.router, prefix="/component", tags=["component"])
api_router.include_router(view.router, prefix="/view", tags=["view"])
api_router.include_router(worker.router, prefix="/worker", tags=["worker"])
api_router.include_router(worker_credential.router, prefix="/worker_credential", tags=["worker_credential"])
api_router.include_router(worker_queue.router, prefix="/worker_queue", tags=["worker_queue"])
api_router.include_router(view_permissions.router, prefix="/view_permissions", tags=["view_permissions"])
api_router.include_router(storage.router, prefix="/storage", tags=["storage"])
api_router.include_router(job.router, prefix="/job", tags=["job"])


@api_router.get("/health")
@api_router.get("/")
def read_root():
    return {"Hello": "Api is alive"}
