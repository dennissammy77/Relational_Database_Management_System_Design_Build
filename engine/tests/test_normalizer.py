import pytest
from engine.normalizer import Normalizer, SelectParts, WhereClause

class TestSelectNormalization:
    def test_normalize_select_normal(self) -> None:
        sql = "SELECT name, age, id FROM users WHERE id = 1"
        normalizer = Normalizer(sql)
        assert normalizer.normalize() == SelectParts(
            columns=["name", "age", "id"],
            table="users",
            where=WhereClause(
                left="id",
                operator="=",
                right=1,
            ),
        )
    
    def test_normalize_select_with_no_where(self) -> None:
        sql = "SELECT name, age, id FROM users"
        normalizer = Normalizer(sql)
        assert normalizer.normalize() == SelectParts(
            columns=["name", "age", "id"],
            table="users",
            where=None,
        )

    def test_normalize_select_with_star(self) -> None:
        sql = "SELECT * FROM users WHERE id = 1"
        normalizer = Normalizer(sql)
        assert normalizer.normalize() == SelectParts(
            columns=["*"],
            table="users",
            where=WhereClause(
                left="id",
                operator="=",
                right=1,
            ),
        )
    
    def test_normalize_select_with_invalid_where(self) -> None:
        sql = "SELECT name, age, id FROM users WHERE id = '1'"
        normalizer = Normalizer(sql)
        assert normalizer.normalize() == SelectParts(
            columns=["name", "age", "id"],
            table="users",
            where=WhereClause(
                left="id",
                operator="=",
                right="1",
            ),
        )

    def test_where_int(self) -> None:
        sql = "SELECT * FROM users WHERE id = 123"
        normalizer = Normalizer(sql)
        assert normalizer.normalize().where.right == 123

    def test_where_float(self) -> None:
        sql = "SELECT * FROM users WHERE price = 12.34"
        normalizer = Normalizer(sql)
        # Note: normalizer uses float() for conversion
        assert normalizer.normalize().where.right == 12.34

    def test_where_bool(self) -> None:
        sql = "SELECT * FROM users WHERE active = true"
        normalizer = Normalizer(sql)
        assert normalizer.normalize().where.right is True
    
    def test_where_str(self) -> None:
        sql = "SELECT * FROM users WHERE name = 'John'"
        normalizer = Normalizer(sql)
        assert normalizer.normalize().where.right == "John"

    def test_case_insensitive(self) -> None:
        sql = "select * from users where id = 1"
        normalizer = Normalizer(sql)
        # We expect it to parse correctly because of `_find_keyword` logic
        assert normalizer.normalize() == SelectParts(
            columns=["*"],
            table="users",
            where=WhereClause(left="id", operator="=", right=1)
        )