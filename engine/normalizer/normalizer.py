import sqlparse
from .select import SelectStatement
from .base import StatementType

class Normalizer:
    def __init__(self, sql: str):
        self.sql = sql
        self.parsed = sqlparse.parse(sql)

    def normalize(self):
        stype = self.get_statement_type()
        if stype == StatementType.SELECT:
            # print("Select statement: ", SelectStatement(self.parsed[0].tokens).normalize())
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