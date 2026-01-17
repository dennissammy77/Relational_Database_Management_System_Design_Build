import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison, Parenthesis
from sqlparse.tokens import Keyword, DML, DDL, Punctuation, Whitespace
from typing import List
from engine.normalizer.base import BaseStatement, CreateParts

class CreateStatement(BaseStatement):
    def normalize(self):
        """
            Extract table name and columns from CREATE statement
        """
        table = self._extract_table_name()
        columns = self._extract_columns()
        print("Table: ", table)
        print("Columns: ", columns)
        return CreateParts(table, columns)

    def _extract_table_name(self) -> str | None:
        """
            Extract table name from CREATE statement
        """
        create_idx = self._find_keyword("TABLE")
        if create_idx == -1:
            return None
        
        for i in range(create_idx + 1, len(self.tokens)):
            token = self.tokens[i]
            if token.ttype in (Keyword, DML, DDL):
                break
            if token.ttype is Whitespace:
                continue
            if isinstance(token, Identifier):
                return self._identifier_name(token)
        return None

    def _extract_columns(self) -> list[str]:
        """
            Extract columns from CREATE statement
            CREATE TABLE table_name (column1 type, column2 type, ...)
        """
        
        column_tokens = self.tokens[self._find_keyword("TABLE") + 2 :]
        if not column_tokens:
            return []

        print("Column tokens: ", column_tokens)
        columns: list[str] = []
        for token in column_tokens:
            if token.ttype in (Keyword, DML, DDL, Punctuation):
                break
            if token.ttype is Whitespace:
                continue
            if isinstance(token, Identifier):
                continue
            if isinstance(token, Parenthesis):
                print("Identifier: ", token)
                for token in token.tokens:
                    print("Token: ", token)
                    name = ""
                    type = ""
                    if isinstance(token, Identifier):
                        name = self._identifier_name(token)
                    elif isinstance(token, DataType):
                        type = token.value.strip()
                    columns.append(ColumnDefParts(name, type))

        print("Columns: ", columns)

        return columns


        
        