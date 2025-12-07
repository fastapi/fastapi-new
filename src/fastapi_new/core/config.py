from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectConfig:
    name: str
    path: Path
    linter: str = "none"
    orm: str = "none"
    python: str | None = None
    structure: str = "simple"
    tests: bool = False
    views: bool = False