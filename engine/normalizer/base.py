from enum import Enum
from dataclasses import dataclass
from typing import Union, Optional
from sqlparse.sql import Identifier, Where, Comparison
from sqlparse.tokens import Keyword, DML, DDL, Punctuation

class StatementType(str, Enum):
    CREATE = "CREATE"
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    DROP = "DROP"
    UNKNOWN = "UNKNOWN"

@dataclass
class WhereClause:
    left: str
    operator: str
    right: Union[str, int, float, bool]

@dataclass
class SelectParts:
    columns: list[str]
    table: str
    where: Optional[WhereClause]

class BaseStatement:
    def __init__(self, tokens: list[any]):
        self.tokens = tokens

    def _find_keyword(self, word: str) -> int:
        """Find keyword in tokens"""
        word = word.upper()
        for i, token in enumerate(self.tokens):
            if token.ttype in (Keyword, DML, DDL) and token.value.upper() == word:
                return i
        return -1

    def _identifier_name(self, ident: Identifier) -> str:
        """Get identifier name"""
        real = ident.get_real_name()
        return real if real else ident.value.strip()

    def _extract_where(self) -> Optional[WhereClause]:
        """
        Extract where clause from statement.
        Handles both compact (id=1) and spaced (id = 1) WHERE clauses.
        """
        where_obj = None
        for token in self.tokens:
            if isinstance(token, Where):
                where_obj = token
                break   

        if where_obj is None:
            return None

        # Try to find a Comparison token (handles cases like "id=1" with no spaces)
        comparison_tokens = [token for token in where_obj.tokens if isinstance(token, Comparison)]

        if len(comparison_tokens) == 1:
            # Case 1: Compact comparison (e.g., "id=1")
            comparison = comparison_tokens[0]
            parts = [part for part in comparison.tokens if not part.is_whitespace and part.ttype is not Punctuation]
            
            if len(parts) < 3:
                raise ValueError("Invalid WHERE clause: insufficient parts in comparison")
                
            left = parts[0].value.strip()
            operator = parts[1].value.strip()
            right_raw = parts[2].value.strip()
        elif len(comparison_tokens) == 0:
            # Case 2: Spaced comparison (e.g., "id = 1" or "active = true")
            # Get all tokens excluding whitespace
            non_whitespace_tokens = [
                token for token in where_obj.tokens 
                if not token.is_whitespace
            ]

            # Skip the WHERE keyword (always first token in Where object)
            comparison_parts = non_whitespace_tokens[1:] if len(non_whitespace_tokens) > 1 else non_whitespace_tokens
            
            if len(comparison_parts) < 3:
                raise ValueError(f"Invalid WHERE clause: insufficient tokens, got {len(comparison_parts)}")
            
            left = comparison_parts[0].value.strip()
            operator = comparison_parts[1].value.strip()
            right_raw = comparison_parts[2].value.strip()
        else:
            raise ValueError(f"Invalid WHERE clause: found {len(comparison_tokens)} comparison tokens")

        # Parse the right operand value
        right: Union[str, int, float, bool]
        if right_raw.startswith("'") and right_raw.endswith("'"):
            # Single-quoted string
            right = right_raw[1:-1]
        elif right_raw.startswith('"') and right_raw.endswith('"'):
            # Double-quoted string
            right = right_raw[1:-1]
        elif right_raw.lower() in ("true", "false"):
            # Boolean value (check before isdigit)
            right = right_raw.lower() == "true"
        elif right_raw.isdigit():
            # Integer
            right = int(right_raw)
        elif right_raw.replace('.', '', 1).isdigit() and right_raw.count('.') <= 1:
            # Float
            right = float(right_raw)
        else:
            # Default to string
            right = right_raw

        return WhereClause(left, operator, right)
