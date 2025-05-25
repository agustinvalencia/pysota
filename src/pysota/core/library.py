from pathlib import Path

import numpy as np
from pydantic import BaseModel, Field
from spacy.language import Language

from pysota.core import Persistence, Publication


class DocsLibrary(BaseModel):
    """
    The implementation of this Store, heavily relies on the fact
    that python dictionaries and lists are ordered and deterministic,
    if this assumption was broken, then logic would have to ensure
    store order by explicitly calling dictionary keys
    """

    folder: Path
    store: dict[str, Publication] = Field(default={})
    prev_lang: Language | None = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def _load_store(self):
        raws = Persistence.load_files(self.folder)
        if len(raws) == 0:
            raise ValueError(f'Persistence load empty \n: {raws}')
        for pub in raws:
            self.store[pub.id] = pub

    def get_document(self, id: str) -> Publication | None:
        pub = self.store.get(id)
        return pub

    def get_ids(self) -> list[str]:
        return list(self.store.keys())

    def get_vectors(self, lang):
        if len(self.store) == 0:
            self._load_store()
        force = self.prev_lang is None or lang != self.prev_lang
        x = [pub.vectorise(lang=lang, force=force) for pub in self.store.values()]
        self.prev_lang = lang
        return np.array(x)
