from typing import TypedDict
from enum import Enum
from dataclasses import dataclass

@dataclass
class DataType(str):
    INT = "INT"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    FLOAT = "FLOAT"
    VARCHAR = "VARCHAR(255)"

@dataclass
class ColumnDefParts:
    name: str
    type: DataType
    constraints: list[str] | None = None