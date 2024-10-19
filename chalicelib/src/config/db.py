import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from chalicelib.src.modules.infrastructure.dto import Base

LOGGER = logging.getLogger('abcall-pqrs-events-microservice')

db_session = None
engine = None

def init_db(migrate=False):
    global db_session
    global engine

    if 'DATABASE_URL' in os.environ:
        if engine is None or db_session is None:
            LOGGER.info(f"Connecting to database at {os.getenv('DATABASE_URL')}")
            try:
                engine = create_engine(os.getenv('DATABASE_URL'), isolation_level="AUTOCOMMIT")
                Session = sessionmaker(bind=engine)
                db_session = Session()
                LOGGER.info("Database connection established.")
                if migrate:
                    import chalicelib.src.modules.infrastructure.dto
                    Base.metadata.create_all(engine)
                    LOGGER.info("Database migrated.")
            except Exception as e:
                LOGGER.error(f"Error establishing database connection: {e}")
                raise e
    else:
        LOGGER.error("DATABASE_URL is not set in environment variables.")
        raise ValueError("DATABASE_URL is not set in environment variables.")

    return db_session
