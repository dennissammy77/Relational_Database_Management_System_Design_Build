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
            print("Select statement: ", self.selectStatement(self.parsed[0].tokens))
    
    def get_statement_type(self) -> StatementType:
        """
            Returns "SELECT", "CREATE"...
        """
        type = self.parsed[0].get_type() or "UNKNOWN"
        try:
            return StatementType(type)
        except ValueError:
            return StatementType.UNKNOWN

    def _find_keyword(self, tokens, word: str) -> int:
        """
            Find keyword in tokens
        """
        word = word.upper()
        for i, token in enumerate(tokens):
            if token.ttype in (Keyword, DML, DDL) and token.value.upper() == word:
                return i
        return -1

    def _identifier_name(self, ident: Identifier) -> str:
        """
            Get identifier name
        """
        real = ident.get_real_name()
        return real if real else ident.value.strip()

    # SELECT PARSER
    def _extract_from_table(self, tokens) -> str | None:
        """
            Extract table name from SELECT statement
        """
        from_idx = self._find_keyword(tokens, "FROM")
        if from_idx == -1:
            return None

        # after FROM, look for identifier
        for i in range(from_idx + 1, len(tokens)):
            token = tokens[i]
            if token.ttype is Whitespace:
                continue
            if isinstance(token, Identifier):
                return self._identifier_name(token)
            if token.ttype in (Keyword, DML, DDL):
                break
        return None
        
    def _extract_columns(self, tokens) -> list[str]:
        """
            Extract columns from SELECT statement
        """
        select_idx = self._find_keyword(tokens, "SELECT")
        from_idx = self._find_keyword(tokens, "FROM")
        if select_idx == -1 or from_idx == -1:
            return []

        middle_tokens = tokens[select_idx + 1: from_idx]
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
    
    def _extract_where(self, tokens) -> Optional[WhereClause]:
        """
            Extract where clause from SELECT statement
        """
        where_obj = None
        for token in tokens:
            if isinstance(token, Where):
                where_obj = token
                break

        if where_obj is None:
            return None
        
        # Find comparison tokens
        comparison_tokens = [token for token in where_obj.tokens if isinstance(token, Comparison)]

        if len(comparison_tokens) != 1:
            raise ValueError("Invalid WHERE clause")

        comparison = comparison_tokens[0]
        parts = [part for part in comparison.tokens if not part.is_whitespace and part.ttype is not Punctuation]
        left = parts[0].value.strip()
        operator = parts[1].value.strip()
        right_raw = parts[2].value.strip()

        right: Union[str, int, float, bool]
        if right_raw.startswith("'") and right_raw.endswith("'"):
            right = right_raw[1:-1]
        elif right_raw.startswith('"') and right_raw.endswith('"'):
            right = right_raw[1:-1]
        elif right_raw.isdigit():
            right = int(right_raw)
        elif right_raw.replace('.', '', 1).isdigit():
            right = float(right_raw)
        elif right_raw.lower() == "true":
            right = True
        elif right_raw.lower() == "false":
            right = False
        else:
            right = right_raw

        return WhereClause(left, operator, right)

    def selectStatement(self, tokens) -> SelectParts:
        """
            Extract columns, table and where clause from SELECT statement
        """
        columns = self._extract_columns(tokens)
        if columns == []:
            columns = ["*"]
        table = self._extract_from_table(tokens)
        if table is None:
            raise ValueError("Table name not found")
        where = self._extract_where(tokens)

        return SelectParts(columns, table, where)