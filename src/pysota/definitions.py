from pydantic import BaseModel
from pathlib import Path
from omegaconf import OmegaConf


class Publication(BaseModel):
    title: str
    year: int
    authors: list[str]
    abstract: str

    def save(self, path: Path):
        dump = OmegaConf.create(self.model_dump())
        filename = f"{self.year}_{self.title}_{self.authors[0]}"
        filename = filename.replace(" ", "_").replace(".", "")
        full_path = path.joinpath(f"{filename}")
        full_path.touch()
        with full_path as f:
            OmegaConf.save(dump,f )


class ResultPage(BaseModel):
    query: str
    total: int
    items_per_page: int
    start_index: int
    items: list[Publication]

    def save(self, path: Path): 
        print( f"creating {path}")
        print(path.iterdir())
        path.mkdir(parents=True, exist_ok=True)
        print( f"created {path}")
        print(path.iterdir())
        for item in self.items:
            item.save(path)


