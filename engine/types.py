from typing import TypedDict
from enum import Enum

class ColumnType(str):
    INT = "INT"
    VARCHAR = "VARCHAR"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    FLOAT = "FLOAT"

Column = TypedDict("Column", {
    "name": str,
    "type": ColumnType,
    "primary_key": bool,
    "unique": bool
})
