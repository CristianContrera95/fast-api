from pathlib import Path  # Python 3.6+ only

from dotenv import load_dotenv

from . import mongodb

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

mongo_instance = mongodb.mongo_class()


import logging  # noqa: E402

from .sqlserverdb import Base, SessionLocal, engine  # noqa: E402

logging.basicConfig(filename="api.log", level=logging.INFO)

# token
from fastapi.security import OAuth2PasswordBearer  # noqa: E402

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# openssl rand -hex 32
SECRET_KEY = "a93c3c46f528ca29b885678f5fe2ac380ad2933ffcd8c300e1b6a5e2f178ad35"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

# Logger
from . import logger_config  # noqa: E402

logger = logger_config.configure_logging()

logger.info("Init app")
