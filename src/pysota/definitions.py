from pydantic import BaseModel
from pathlib import Path
from omegaconf import OmegaConf


class Publication(BaseModel):
    title: str
    year: int
    authors: list[str]
    abstract: str

    def save(self, path: Path) -> None:
        self.process_abstract()
        dump = OmegaConf.create(self.model_dump())
        filename = f"{self.year}__{self.clean_string(self.title)}__{self.clean_string(self.authors[0])}.yaml"
        full_path = path.joinpath(filename)
        full_path.touch()
        with full_path as f:
            OmegaConf.save(dump, f)
            print(f"- {filename}")

    def clean_string(self, msg: str) -> str:
        remove_chars_map = {
            ": ": "-",
            "\n ": "",
            "\n": "",
            " ": "_",
            ".": "_",
            ",": "_",
            "?": "",
            "!": "",
            "$": "",
            "\\": "",
        }
        for char, replacement in remove_chars_map.items():
            msg = msg.replace(char, replacement)
        return msg

    def process_abstract(self):
        self.abstract = self.abstract.replace("\n", " ")


class ResultPage(BaseModel):
    query: str
    total: int
    items_per_page: int
    start_index: int
    items: list[Publication]

    def save(self, path: Path):
        path = path.joinpath(self.query.replace(" ", "_"))
        path.mkdir(parents=True, exist_ok=True)
        print(f"Saving results to {path}")
        for item in self.items:
            item.save(path)
