import os

import uvicorn
from fastapi import FastAPI

from api.middleware import cross_origin, trustedhost
from api.router import api_router
from app import Base, SessionLocal, engine, logger

Base.metadata.create_all(bind=engine)
ENV = os.getenv("ENVIRONMENT")

# init instance
app = FastAPI()

# routes
app.include_router(api_router)

# middlewares
if ENV and ENV.upper() == "PROD":
    trustedhost.add_trusted_host_middleware(app)
cross_origin.add_cross_origin_middleware(app)


@app.on_event("shutdown")
def shutdown():
    handle_cleanup()


def handle_cleanup():
    logger.info("Closing all connections")
    SessionLocal.close_all()
    engine.dispose()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
