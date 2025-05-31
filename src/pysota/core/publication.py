import re
import textwrap
from functools import cached_property
from pathlib import Path

import numpy as np
import numpy.typing as npt
from omegaconf import OmegaConf
from pydantic import BaseModel, PrivateAttr, computed_field


class Publication(BaseModel):
    title: str
    year: int
    authors: list[str]
    internal_index: int
    provider_name: str
    query_name: str
    abstract: str
    _vectors: npt.ArrayLike = PrivateAttr(default=np.array([]))

    class Config:
        arbitrary_types_allowed = True

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

    def save(self, path: Path) -> None:
        self.abstract = self.clean_text(self.abstract)
        self.title = self.clean_text(self.title)
        dump = OmegaConf.create(self.model_dump())
        filename = self.id
        full_path = path.joinpath(f'{filename}.yaml')
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

    # Used GPT to come up with these regex
    def clean_text(self, text: str) -> str:
        # Remove LaTeX document class and package inclusions
        text = re.sub(r'\\documentclass\[.*?\]\{.*?\}\s*\\usepackage\{.*?\}', '', text)
        text = re.sub(r'\\setlength\{.*?\}\{.*?\}', '', text)

        # Remove \begin{document}...\end{document} blocks and their content
        # This is more robust as it removes the content as well.
        text = re.sub(r'\\begin\{document\}.*?\\end\{document\}', '', text, flags=re.DOTALL)

        # Remove common LaTeX math environments like $$...$$
        text = re.sub(r'\$\$.*?\$\$', '', text, flags=re.DOTALL)

        # Remove any remaining common LaTeX commands that might appear outside environments
        # This regex handles the `\something{another}` pattern.
        text = re.sub(r'\\[a-zA-Z]+\{[^\}]*\}', '', text)
        # This handles `\something` (commands without arguments).
        text = re.sub(r'\\[a-zA-Z]+', '', text)

        # Remove common LaTeX symbols like % that might be escaped
        text = text.replace('\%', '')

        # map multiple spaces to single space
        text = re.sub(r'\s+', ' ', text)
        # remove HTML tags if any (from previous version)
        text = re.sub(r'<.*?>', '', text)
        # remove leading 'abstract' keyword (from previous version)
        text = re.sub(r'^\s*abstract\s*', '', text, flags=re.IGNORECASE)

        # Strip leading and trailing whitespace again after all replacements
        text = text.strip()
        return text

    def vectorise(self, lang, force=False):
        if self._vectors is None or force:
            self._vectors = lang(self.abstract).vector
        return self._vectors

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
