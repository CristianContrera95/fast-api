from fastapi.middleware.trustedhost import TrustedHostMiddleware


def add_trusted_host_middleware(app):
    origins = ["*.azurewebsites.net", "localhost", "127.0.0.1", "0.0.0.0"]
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=origins)
