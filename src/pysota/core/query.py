from abc import ABC, abstractmethod
from pathlib import Path

from omegaconf import OmegaConf
from pydantic import BaseModel, Field


class IQuery(BaseModel, ABC):
    name: str = Field(..., frozen=True)
    provider: str = Field(..., frozen=True)
    base: str = Field(..., frozen=True)
    include: list[str] = Field(..., frozen=True)
    exclude: list[str] = Field(..., frozen=True)
    items_per_page: int = Field(..., frozen=True)
    start_index: int = Field(..., frozen=True)

    @abstractmethod
    def generate_url(self) -> str:
        raise NotImplementedError

    def save_query(self, path: Path) -> None:
        dump = OmegaConf.create(self.model_dump())
        filename = f'{self.name}.yaml'
        full_path = path.joinpath(filename)
        if full_path.exists():
            return
        full_path.touch()
        with full_path as f:  # type: ignore
            OmegaConf.save(dump, f)
