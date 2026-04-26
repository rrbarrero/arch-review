from enum import StrEnum, auto


class ProcessingStatus(StrEnum):
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()


class ChunkStatus(StrEnum):
    PENDING = auto()
    EMBEDDED = auto()
    GRAPH_PROCESSED = auto()
    FAILED = auto()
