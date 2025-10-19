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
from app.models.school import School

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_cities(session: Session) -> None:
    """Init cities if they don't exist"""
    # Do not delete existing cities here. Instead, load existing ids/names
    # and only add new cities from CSV. This makes the import idempotent
    # and prevents duplicate primary key insert attempts.

    csv_file = Path(__file__).parent.parent / "data" / "cities_prepaired.csv"

    if not csv_file.exists():
        logger.warning(f"Cities CSV file not found at {csv_file}")
        return

    try:
        # Use utf-8-sig to handle possible BOM and delimiter=';' for the provided CSV
        with open(csv_file, mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file, delimiter=';', skipinitialspace=True)
            cities = []
            for row in csv_reader:
                # Normalize keys to handle unexpected capitalization
                # and safely extract id and name values
                row_normalized = {k.strip().lower(): (v or '').strip() for k, v in row.items()}

                name = row_normalized.get('name')
                if not name:
                    # If name column missing, try to fall back to the second column value
                    values = [v for v in row.values() if v is not None]
                    if len(values) >= 2:
                        name = values[1].strip()
                if not name:
                    # skip malformed rows without a name
                    continue

                id_value = None
                id_raw = row_normalized.get('id')
                if id_raw:
                    try:
                        id_value = int(id_raw)
                    except ValueError:
                        id_value = None

                if id_value is not None:
                    city = City(id=id_value, name=name)
                else:
                    city = City(name=name)

                cities.append(city)

            if cities:
                # Avoid inserting cities that would conflict with existing primary keys
                # Collect existing ids from DB and skip any CSV rows whose id already exists.
                existing_ids = set()
                try:
                    rows = session.exec(select(City)).all()
                    for c in rows:
                        if getattr(c, 'id', None) is not None:
                            existing_ids.add(c.id)
                except Exception:
                    # If we can't read existing cities (fresh DB), treat as empty
                    existing_ids = set()

                cities_to_add = []
                for city in cities:
                    cid = getattr(city, 'id', None)
                    if cid is not None and cid in existing_ids:
                        # Skip city with id that already exists
                        continue
                    # If id is missing, or id is new, add the city (we don't dedupe by name)
                    cities_to_add.append(city)

                if cities_to_add:
                    session.add_all(cities_to_add)
                    session.commit()
                    logger.info(f"Cities initialized: {len(cities_to_add)} new entries added")
                else:
                    logger.info("No new cities to initialize (all present or conflicts skipped)")
            else:
                logger.info("No valid city rows found in CSV; nothing to initialize")
    except Exception as e:
        logger.error(f"Error init cities: {e}")
        session.rollback()
        raise

def init_schools(session: Session) -> None:
    """Import schools from app/data/schools_processed.csv.

    CSV format is expected: id;name;city_id (semicolon-delimited)
    Dedupe by id only: if a school id exists in DB, skip that row.
    If city_id is present but no City with that id exists, city_id will be set to None.
    """
    csv_file = Path(__file__).parent.parent / "data" / "schools_prepaired.csv"

    if not csv_file.exists():
        logger.info(f"Schools CSV not found at {csv_file}; skipping schools import")
        return

    try:
        with open(csv_file, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';', skipinitialspace=True)
            schools = []
            for row in reader:
                # Normalize keys
                row_norm = {k.strip().lower(): (v or '').strip() for k, v in row.items()}
                id_raw = row_norm.get('id') or ''
                name = row_norm.get('name') or ''
                city_raw = row_norm.get('city_id') or row_norm.get('city') or ''

                if not name:
                    # skip malformed rows
                    continue

                sid = None
                try:
                    sid = int(id_raw) if id_raw != '' else None
                except ValueError:
                    sid = None

                city_id = None
                try:
                    city_id = int(city_raw) if city_raw != '' else None
                except ValueError:
                    city_id = None

                school = School(name=name, city_id=city_id) if sid is None else School(id=sid, name=name, city_id=city_id)
                schools.append(school)

            if not schools:
                logger.info("No school rows found in CSV; skipping")
                return

            # Load existing school ids to avoid duplicates
            existing_ids = set()
            try:
                rows = session.exec(select(School)).all()
                for s in rows:
                    if getattr(s, 'id', None) is not None:
                        existing_ids.add(s.id)
            except Exception:
                existing_ids = set()

            to_add = []
            for sch in schools:
                if getattr(sch, 'id', None) is not None and sch.id in existing_ids:
                    continue
                # If city_id present but city doesn't exist, clear it
                if getattr(sch, 'city_id', None) is not None:
                    city_exists = session.exec(select(City).where(City.id == sch.city_id)).first()
                    if not city_exists:
                        sch.city_id = None
                to_add.append(sch)

            if to_add:
                session.add_all(to_add)
                session.commit()
                logger.info(f"Schools initialized: {len(to_add)} new entries added")
            else:
                logger.info("No new schools to initialize (all present or skipped)")
    except Exception as e:
        logger.error(f"Error init schools: {e}")
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

    # Initialize schools after tables are present
    try:
        with Session(engine) as s:
            # Ensure cities are initialized first so school.city_id references can be resolved
            init_cities(s)
            init_schools(s)
    except Exception:
        # Don't fail hard here; init_schools logs its own errors
        logger.exception("Error while initializing schools")

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