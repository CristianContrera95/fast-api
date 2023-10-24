from fastapi.middleware.cors import CORSMiddleware


def add_cross_origin_middleware(app):
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
    )
