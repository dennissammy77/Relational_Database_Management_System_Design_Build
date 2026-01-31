import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison, Parenthesis
from sqlparse.tokens import Keyword, DML, DDL, Punctuation, Whitespace
from typing import List
from engine.normalizer.base import BaseStatement, CreateParts
from engine.types import DataType, ColumnDefParts

class CreateStatement(BaseStatement):
    columns: list[ColumnDefParts]
    
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
        raise ValueError("Table name not found")

    def _extract_columns(self) -> list[str]:
        """
            Extract columns from CREATE statement
            CREATE TABLE table_name (column1 type, column2 type, ...)
        """
        
        column_tokens = self.tokens[self._find_keyword("TABLE") + 2 :]
        if not column_tokens or len(column_tokens) < 2:
            raise ValueError("Columns not found")

        # print("Column tokens: ", column_tokens)
        columns: list[ColumnDefParts] = []
        for token in column_tokens:
            if token.ttype in (Keyword, DML, DDL, Punctuation):
                break
            if token.ttype is Whitespace:
                continue
            if isinstance(token, Identifier):
                continue
            if isinstance(token, Parenthesis):
                # print("Parenthesis: ", token)
                column_def_parts: list[ColumnDefParts] = []
                for token in token.tokens:
                    if token.value == '(' or token.value == ')':
                        continue
                    if token.ttype is Whitespace:
                        continue
                    if isinstance(token, Identifier):
                        if self._identifier_name(token) in [col.name for col in column_def_parts]:
                            raise ValueError("Duplicate column name")
                        column_def_parts.append(ColumnDefParts(self._identifier_name(token), ""))
                    if token.value in [DataType.INT, DataType.TEXT, DataType.BOOLEAN, DataType.DATE, DataType.FLOAT]:
                        if column_def_parts:
                            column_def_parts[-1].type = token.value.strip()
                    if isinstance(token, Comparison):
                        continue
                    if isinstance(token, Parenthesis):
                        continue
                    if isinstance(token, IdentifierList):
                        continue
                # print("Column def parts: ", column_def_parts)
                columns.extend(column_def_parts )
        # print("Columns: ", columns)
        self._validate_columns(columns)
        return columns

        
        