import pytest
from engine.normalizer.normalizer import Normalizer
from engine.normalizer.base import SelectParts, WhereClause, CreateParts
from engine.types import ColumnDefParts

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

class TestCreateNormalization:
    def test_create_table_missing_name(self) -> None:
        """
        Test that the create table statement raises an error if the table name is missing
        """
        sql = "CREATE TABLE (id INT, name TEXT)"
        normalizer = Normalizer(sql)
        with pytest.raises(ValueError):
            normalizer.normalize()

    def test_create_table_no_columns(self) -> None:
        """
        Test that the create table statement raises an error if there are no columns
        """
        sql = "CREATE TABLE users"
        normalizer = Normalizer(sql)
        with pytest.raises(ValueError):
            normalizer.normalize()

    def test_create_table(self) -> None:
        """
        Test that the create table statement is normalized correctly
        """
        sql = "CREATE TABLE users (id INT, name TEXT)"
        normalizer = Normalizer(sql)
        assert normalizer.normalize() == CreateParts(
            table="users",
            columns=[
                ColumnDefParts(name="id", type="INT", constraints=None),
                ColumnDefParts(name="name", type="TEXT", constraints=None)
            ],
        )

    def test_create_table_with_same_column_name(self) -> None:
        """
        Test that the create table statement raises an error if there are duplicate column names
        """
        sql = "CREATE TABLE users (id INT, name TEXT, id TEXT)"
        normalizer = Normalizer(sql)
        with pytest.raises(ValueError):
            normalizer.normalize()

    def test_create_table_with_column_missing_type(self) -> None:
        """
        Test that the create table statement raises an error if there is a missing type
        """
        sql = "CREATE TABLE users (id, name)"
        normalizer = Normalizer(sql)
        with pytest.raises(ValueError):
            normalizer.normalize()
    