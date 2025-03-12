from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, List, Optional, Type
from omegaconf import OmegaConf
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field as SQLField, create_engine, Session


# --- Define a configuration model ---
class DBConfig(BaseModel):
    database_url: str = 'sqlite:///database.db'
    echo: bool = False


# --- Define a SQLModel for a scientific article ---
class ScientificArticle(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    title: str
    authors: str  # Authors will be stored as a comma-separated string
    year: int


# --- Define the DBManager as a Pydantic model ---
class DBManager(BaseModel):
    config: DBConfig
    engine: Optional[Any] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.engine = create_engine(self.config.database_url, echo=self.config.echo)
        # Create all tables defined via SQLModel (including ScientificArticle)
        SQLModel.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of operations.
        The return type is annotated as a Generator[Session, None, None]
        to satisfy type checkers.
        """
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception as exc:
            session.rollback()
            raise exc
        finally:
            session.close()

    def add(self, obj: SQLModel) -> SQLModel:
        """Add a new record to the database and refresh it."""
        with self.get_session() as session:
            session.add(obj)
            session.commit()  # Extra commit safety
            session.refresh(obj)
            return obj

    def get(self, model: Type[SQLModel], record_id: int) -> Optional[SQLModel]:
        """Retrieve a single record by primary key."""
        with self.get_session() as session:
            return session.get(model, record_id)

    def delete(self, obj: SQLModel) -> None:
        """Delete a record from the database."""
        with self.get_session() as session:
            session.delete(obj)

    def query_all(self, model: Type[SQLModel]) -> List[SQLModel]:
        """Return all records of a given model."""
        with self.get_session() as session:
            return session.query(model).all()

    def create_database_from_folder(self, folder: Path) -> int:
        """
        Scans the given folder for YAML files and populates the database with ScientificArticle records.
        Assumes each YAML file contains keys: title, authors, and year.
        Returns the number of articles added.
        """
        count = 0
        for yaml_file in folder.glob('*.yaml'):
            yaml = OmegaConf.load(yaml_file)
            data = OmegaConf.to_container(yaml)
            print(data)
        return count
