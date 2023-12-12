from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://xdkxfsvq:jMaYoiqyb-KtqDGG6MloQZ6QJ0N4mJ_d@suleiman.db.elephantsql.com/xdkxfsvq"
# SQLALCHEMY_DATABASE_URL = "postgres://xwfhkrle:aj3keFy25QHvuY0KPVOEMvi4ow_KUD6q@berry.db.elephantsql.com/xwfhkrle"

# just for debug in local > don't use in prod
# logging.basicConfig()
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
#engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
