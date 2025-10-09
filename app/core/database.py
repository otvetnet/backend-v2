import logging
import csv
from pathlib import Path

from sqlmodel import Session, create_engine, select

from app.core.config import settings

from app.models.user import User
from app.models.city import City
from app.models.survey import Survey
from app.models.survey import Question
from app.models.survey import AnswerOption
from app.models.survey import SurveyResponse
from app.models.game import Game, Scene

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_cities(session: Session) -> None:
    """Init cities if they don't exist"""
    existing_cities = session.exec(select(City)).first()
    if existing_cities:
        logger.info("Cities are ok, skipping init...")
        return

    csv_file = Path(__file__).parent.parent / "data" / "prepared_cities.csv"

    if not csv_file.exists():
        logger.warning(f"Cities CSV file not found at {csv_file}")
        return

    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            cities = []
            for row in csv_reader:
                city = City(name=row['name'])
                cities.append(city)

            session.add_all(cities)
            session.commit()

            logger.info(f"Cities initialized: {len(cities)} total")
    except Exception as e:
        logger.error(f"Error init cities: {e}")
        session.rollback()
        raise


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    SQLModel.metadata.create_all(engine)

    # user = session.exec(
    #     select(User).where(User.email == settings.FIRST_SUPERUSER)
    # ).first()
    # if not user:
    #     user_in = UserCreate(
    #         email=settings.FIRST_SUPERUSER,
    #         password=settings.FIRST_SUPERUSER_PASSWORD,
    #         is_superuser=True,
    #     )
    #     user = crud.create_user(session=session, user_create=user_in)