from typing import List

Column = {
    name: str,
    type: str,
    primary_key: bool,
    unique: bool
}

class Table:
    def __init__(self, name: str, columns: list[Column]):
        self.name = name
        self.columns = columns
        self.rows = []

class Database:
    def __init__(self):
        self.tables = {}

    def create_table(self, table_name: str, columns: list[Column]):
        if table_name in self.tables:
            raise Exception(f"Table {table_name} already exists")
        self.tables[table_name] = Table(table_name, columns)
        return self.tables[table_name]


    def drop_table(self, table_name: str):
        if table_name not in self.tables:
            raise Exception(f"Table {table_name} does not exist")
        del self.tables[table_name]
        return True
    
    def get_table(self, table_name: str):
        if table_name not in self.tables:
            raise Exception(f"Table {table_name} does not exist")
        return self.tables[table_name]
    
    def get_tables(self):
        return self.tables
    