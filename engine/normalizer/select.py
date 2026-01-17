from sqlparse.sql import IdentifierList, Identifier, Where, Comparison
from sqlparse.tokens import Keyword, DML, DDL, Whitespace, Punctuation, Wildcard
from typing import List
from engine.normalizer.base import BaseStatement, SelectParts

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