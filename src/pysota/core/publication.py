import re
import textwrap
from functools import cached_property
from pathlib import Path

from omegaconf import OmegaConf
from pydantic import BaseModel, computed_field


class Publication(BaseModel):
    title: str
    year: int
    authors: list[str]
    internal_index: int
    provider_name: str
    query_name: str
    abstract: str

    @computed_field
    @cached_property
    def id(self) -> str:
        return f'{self.query_name}-{self.provider_name.lower()}-{self.internal_index:03d}'

    def check_validity(self):
        if not self.year > 0:
            return False, f'year = {self.year}'
        elif not len(self.authors) > 0:
            return False, f'{self.authors=}'
        elif not len(self.title) > 0:
            return False, f'{self.title=}'
        elif not len(self.abstract) > 100:
            return False, f'{self.abstract=}'
        return True, ''

    def save(self, path: Path, include_index: bool = False) -> None:
        self.abstract = self.clean_text(self.abstract)
        self.title = self.clean_text(self.title)
        dump = OmegaConf.create(self.model_dump())
        if include_index:
            filename = f'{self.internal_index:03d}__{self}.yaml'
        else:
            filename = f'{self}.yaml'
        full_path = path.joinpath(filename)
        full_path.touch()
        with full_path as f:  # type: ignore
            OmegaConf.save(dump, f)

    def clean_title(self, text: str) -> str:
        # remove unsafe characters for filename
        remove_chars_map = {
            '-': '',
            ': ': '-',
            '.': '_',
            ' ': '_',
            '_-': '_',
            '-_': '_',
            ',': '_',
            '?': '',
            '!': '',
            '$': '',
            '\\': '',
            '/': '',
            "'": '',
            '"': '',
        }
        for char, replacement in remove_chars_map.items():
            text = text.replace(char, replacement)

        # replace multiple underscores with single underscore
        text = re.sub(r'_+', '_', text)
        text = re.sub(r'-+', '-', text)
        # strip leading and trailing spaces
        text = text.strip('_')
        return text

    def clean_text(self, text):
        # map multiple spaces to single space
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'<.*?>', '', text)
        text = re.sub(r'^\s*abstract\s*', '', text, flags=re.IGNORECASE)
        return text

    def __str__(self):
        name = self.clean_text(self.title)
        name = self.clean_title(name)
        name = textwrap.shorten(name, width=60, placeholder='')
        authors = self.clean_text(self.authors[0])
        authors = self.clean_title(authors)
        return f'{self.year}-{name}-{authors}'

    def __eq__(self, other):
        return (
            self.year == other.year
            and set(self.authors) == set(other.authors)
            and self.title == other.title
        )
