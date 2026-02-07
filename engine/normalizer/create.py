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
        print("Column tokens: ", column_tokens)
        if not column_tokens:
            return []
        if len(column_tokens) == 1:
            raise ValueError("Column name not found")

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

                middle_tokens = token.tokens[1:-1]
                print("Parenthesis: ", middle_tokens) 
                # TODO: 
                # 1. Extract column name
                # 2. Extract column type
                # 3. Extract column constraints
                # 4. Validate column
                # 5. Add column to column_def_parts
                # 6. Check if type is missing
                # 7. Check if column name is missing

                column_def_parts: list[ColumnDefParts] = []
                for token in token.tokens:
                    if token.value == '(' or token.value == ')':
                        continue
                    if token.ttype is Whitespace:
                        continue
                    if isinstance(token, Identifier):
                        print("Identifier: ", token)
                        col_name = self._identify_column_name(token)
                        if self._identifier_name(token) in [col.name for col in column_def_parts]:
                            raise ValueError("Duplicate column name")
                        column_def_parts.append(ColumnDefParts(self._identifier_name(token), ""))
                    if token.value in [DataType.INT, DataType.TEXT, DataType.BOOLEAN, DataType.DATE, DataType.FLOAT]:
                        print("DataType: ", token)
                        if column_def_parts:
                            column_def_parts[-1].type = token.value.strip()
                    if isinstance(token, Comparison):
                        continue
                    if isinstance(token, Parenthesis):
                        continue
                    if isinstance(token, IdentifierList):
                        for identifier in token.get_identifiers():
                            col_name = self._identify_column_name(identifier)
                            if col_name in [col.name for col in column_def_parts]:
                                raise ValueError("Duplicate column name")
                            column_def_parts.append(ColumnDefParts(col_name, ""))
                        
                err_msg = self._validate_columns(column_def_parts)
                if not err_msg:
                    columns.extend(column_def_parts)
                else:
                    raise ValueError(err_msg)
        return columns

    def _validate_columns(self, columns: list[ColumnDefParts]):
        """
            Validate columns if name and type are present
        """
        print("Validating columns: ", columns)
        err_msg = ""
        for column in columns:
            if not column.name:
                err_msg += f"Column name is missing for column {column}, "
            if not column.type:
                err_msg += f"Column type is missing for column {column.name}, "

        if err_msg:
            print("Error in columns: ", err_msg)
            return err_msg
        return None
        
    def _identify_column_name(self, token: Identifier) -> str:
        """
            Identify column name from token
        """
        return self._identifier_name(token)