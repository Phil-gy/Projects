import os

from sqlalchemy import inspect, text
from sqlmodel import SQLModel, Session, create_engine


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./recipes.db")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {},
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def migrate_database():
    inspector = inspect(engine)
    columns = [column["name"] for column in inspector.get_columns("recipe")]

    with engine.begin() as connection:
        if "rating" not in columns:
            if DATABASE_URL.startswith("sqlite"):
                connection.execute(text("ALTER TABLE recipe ADD COLUMN rating FLOAT"))
            else:
                connection.execute(
                    text("ALTER TABLE recipe ADD COLUMN rating DOUBLE PRECISION")
                )
        else:
            if not DATABASE_URL.startswith("sqlite"):
                connection.execute(
                    text(
                        "ALTER TABLE recipe "
                        "ALTER COLUMN rating TYPE DOUBLE PRECISION "
                        "USING rating::DOUBLE PRECISION"
                    )
                )


def get_session():
    with Session(engine) as session:
        yield session