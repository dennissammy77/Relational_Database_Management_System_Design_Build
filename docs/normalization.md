SQL Normalization Step

The normalizer ensures that semantically equivalent SQL statements result in the same internal structure. It converts raw SQL strings into a structured format that can be used by the query planner.

Why a normalizer?
SQL is a declarative language, meaning that the order of clauses does not matter. For example, the following statements are semantically equivalent:

SELECT * FROM users WHERE id = 1
SELECT id, name FROM users WHERE id = 1
SELECT name, id FROM users WHERE id = 1

Without a normalizer, the query planner would have to deal with all of these different representations. With a normalizer, the query planner only has to deal with one representation.

Input and Output Contract
Input
`A raw SQL string`
Internally processed using sqlparse.parse(sql) to obtain a grouped token tree
Output
`A normalized statement parts object, specific to the statement type`

Example output for a SELECT statement:

`
SelectParts(
 columns = ["id", "name"],
 table   = "users",
 where   = WhereClause(left="id", operator="=", right=1)
)
`

This object contains only the information required to understand what the query wants, not how to execute it.

Supported SQL Statement Types
- SELECT
- INSERT
- UPDATE
- DELETE

SELECT
- Column lists (SELECT id, name)
- Wildcards (SELECT *)
- Single table (FROM users)
- Optional WHERE clause

WHERE restrictions:
- Exactly one comparison
- Equality operator only (=)
- Literal values (string, int, float, boolean)

Example supported queries:
```sql
SELECT * FROM users;
SELECT id, name FROM users WHERE id = 1;
```
Unsupported queries:
- Multi-table queries
- Subqueries
- Joins
- Aggregations

Why not a tokenizer?
A tokenizer produces a flat stream of atomic symbols. However:
- sqlparse already performs tokenization and grouping
- Re-tokenizing would duplicate effort
- The project goal is database engine understanding, not lexer implementation