import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison, Parenthesis
from sqlparse.tokens import Keyword, DML, DDL, Punctuation, Whitespace
from typing import List
from engine.normalizer.base import BaseStatement, CreateParts
from engine.types import DataType, ColumnDefParts

class CreateStatement(BaseStatement):
    columns: list[ColumnDefParts] = []
    column_chunks: list[list] = []

    """
        TODO: 
        1. VARCCHAR test is failing
    """
    
    def normalize(self):
        """
            Extract table name and columns from CREATE statement
        """
        self.columns = []
        self.column_chunks = []
        table = self._extract_table_name()
        columns = self._extract_columns()
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
            1. Find the index of TABLE keyword
            2. Find the parenthesis tokens
            3. Extract the column name and type
            4. Validate the column name and type
            5. Add the column to the columns list

        """
        table_idx = self._find_keyword("TABLE")
        # loop through tokens to find the parenthesis if not found raise error
        parenthesis_idx = -1
        
        for i in range(table_idx + 1, len(self.tokens)):
            token = self.tokens[i]
            if token.ttype in (Keyword, DML, DDL):
                break
            if token.ttype is Whitespace:
                continue
            if isinstance(token, Identifier):
                continue
            if isinstance(token, Parenthesis):
                parenthesis_idx = i
                break
        if parenthesis_idx == -1:
            raise ValueError("Parenthesis not found")
        column_tokens = self.tokens[parenthesis_idx:]
        print("Column tokens: ", column_tokens)
        if not column_tokens:
            raise ValueError("Column tokens not found")

        for token in column_tokens:
            if token.ttype in (Keyword, DML, DDL, Punctuation):
                break
            if token.ttype is Whitespace:
                continue
            if isinstance(token, Identifier):
                continue
            if isinstance(token, Parenthesis):
                self._extract_parenthesis(token)

        err_msg = self._validate_columns()
        if err_msg:
            raise ValueError(err_msg)

        return self.columns

    def _extract_parenthesis(self, token: Parenthesis) -> list[ColumnDefParts]:
        """
            Extract parenthesis tokens
            1. remove first and last token
            2. extract column name and type
            3. validate column name and type
            4. add column to column_def_parts
        """
        middle_tokens = token.tokens
        first_token = middle_tokens[0]
        last_token = middle_tokens[-1]
        if first_token.value == "(" and last_token.value == ")":
            middle_tokens = middle_tokens[1:-1]

        if isinstance(middle_tokens[0], IdentifierList):
            for token in middle_tokens[0].get_identifiers():
                col_name = self._identifier_name(token)
                if col_name in [col.name for col in self.columns]:
                    raise ValueError("Duplicate column name")
                self.columns.append(ColumnDefParts(col_name, ""))

        else:
            token_chunks = self.split_on_commas_chunks(middle_tokens)
            for i, chunk in enumerate(token_chunks):
                print(f"Chunk {i}: ", chunk)
                
            for chunk in token_chunks:
                for token in chunk:
                    if isinstance(token, Identifier):
                        col_name = self._identifier_name(token)
                        if col_name in [col.name for col in self.columns]:
                            raise ValueError("Duplicate column name")
                        self.columns.append(ColumnDefParts(col_name, ""))
                    if token.value in [DataType.INT, DataType.TEXT, DataType.BOOLEAN, DataType.DATE, DataType.FLOAT, DataType.VARCHAR]:
                        self.columns[-1].type = token.value.strip()

    def split_on_commas_chunks(self, tokens):
        """
            Split tokens on commas
        """
        current_chunk = []
        depth = 0
        for char in tokens:
            print("Char: ", char.value)
            if char.value == "(":
                depth += 1
                current_chunk.append(char)
            if char.value == ")":
                depth -= 1
                current_chunk.append(char)
            if char.value == "," and depth == 0:
                self.column_chunks.append(current_chunk)
                current_chunk = []
            else:
                current_chunk.append(char)
        
            print("Current chunk: ", current_chunk)
            print("Depth: ", depth)
            
        if current_chunk:
            self.column_chunks.append(current_chunk)

        return self.column_chunks
    
    def _validate_columns(self):
        """
            Validate columns if name and type are present
        """
        # print("Validating columns: ", columns)
        err_msg = ""
        for column in self.columns:
            if not column.name:
                err_msg += f"Column name is missing for column {column}, "
            if not column.type:
                err_msg += f"Column type is missing for column {column.name}, "

        if err_msg:
            # print("Error in columns: ", err_msg)
            return err_msg
        return None
