from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    filename: str
    content_type: str
    size_bytes: int
