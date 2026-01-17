import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison
from sqlparse.tokens import Keyword, DML, DDL, Whitespace, Punctuation, Wildcard
from enum import Enum
from dataclasses import dataclass
from typing import Union, Optional, List

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

class Normalizer:
    def __init__(self, sql: str):
        self.sql = sql
        self.parsed = sqlparse.parse(sql)

    def normalize(self):
        stype = self.get_statement_type()
        if stype == StatementType.SELECT:
            # print("Select statement: ", self.selectStatement(self.parsed[0].tokens))
            # return self.selectStatement(self.parsed[0].tokens)
            print("Select statement: ", SelectStatement(self.parsed[0].tokens).normalize())
            return SelectStatement(self.parsed[0].tokens).normalize()

    def get_statement_type(self) -> StatementType:
        """
            Returns "SELECT", "CREATE"...
        """
        type = self.parsed[0].get_type() or "UNKNOWN"
        try:
            return StatementType(type)
        except ValueError:
            return StatementType.UNKNOWN

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

class SelectStatement(BaseStatement):
    def normalize(self):
        """
            Extract columns, table and where clause from SELECT statement
        """
        columns = self._extract_columns()
        if columns == []:
            columns = ["*"]
        table = self._extract_from_table()
        if table is None:
            raise ValueError("Table name not found")
        where = self._extract_where()

        return SelectParts(columns, table, where)
    
    def _extract_columns(self) -> list[str]:
        """
            Extract columns from SELECT statement
        """
        select_idx = self._find_keyword("SELECT")
        from_idx = self._find_keyword("FROM")
        if select_idx == -1 or from_idx == -1:
            return []

        middle_tokens = self.tokens[select_idx + 1: from_idx]
        if not middle_tokens:
            return []

        if middle_tokens[0].ttype is Wildcard:
            return ["*"]

        columns: List[str] = []
        # after SELECT, look for identifier
        for token in middle_tokens:
            if token.ttype in (Keyword, DML):
                break
            if token.ttype is Whitespace:
                continue
            if token.ttype is Punctuation:
                continue
            if token.ttype is Wildcard:
                continue
            if isinstance(token, Comparison):
                continue
            if isinstance(token, IdentifierList):
                for ident in token.get_identifiers():
                    columns.append(self._identifier_name(ident))
            if isinstance(token, Identifier):
                columns.append(self._identifier_name(token))
        return columns

    def _extract_from_table(self) -> str | None:
        """
            Extract table name from SELECT statement
        """
        from_idx = self._find_keyword("FROM")
        if from_idx == -1:
            return None

        # after FROM, look for identifier
        for i in range(from_idx + 1, len(self.tokens)):
            token = self.tokens[i]
            if token.ttype in (Keyword, DML, DDL):
                break
            if token.ttype is Whitespace:
                continue
            if isinstance(token, Identifier):
                return self._identifier_name(token)
        return None