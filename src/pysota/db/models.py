from sqlmodel import SQLModel, Field
from pathlib import Path


class Article(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    author: list[str]
    path: Path


class Author(SQLModel, table=True):
    name: str = Field(default=None, primary_key=True)
    article: list[Article]
