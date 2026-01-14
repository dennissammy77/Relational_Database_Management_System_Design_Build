# Building a Relational Database Management System (RDBMS)

## Project Overview 
The goal of this project is to design and implement a simple relational database management system (RDBMS) with:

- A SQL-like interface
- Support for basic relational concepts (tables, keys, joins)
- An interactive REPL
- A demonstration web application that uses the database for CRUD operations

This project is intentionally scoped to focus on core database fundamentals, clarity of design, and explainability rather than production-level completeness.

All database functionality will be implemented from scratch, without using:
- SQLite
- ORMs
- Existing SQL engines or parsers

This ensures the project demonstrates real understanding rather than library usage.

## Key Principles
- Small but correct
- Explicit trade-offs
- Readable and testable code
- Clear separation of concerns

### Intentional Omissions
- Transactions
- Query optimization
- Advanced SQL features
- Concurrency control

These are excluded to keep the system understandable and well-implemented within the challenge scope.

## High - Level Design
/rdbms
    |__ engine/
    |__ storage/
    |__ repl/
    |__ api/
    |__ web/
    |__ tests/
    |__ docs/
    |__ .gitignore
    |__ README.md

### Core components
- Table
    Holds Rows and enforces schema and constraints
- Column
    Defines data type and constraints
- Row
    Collection of values
- Index
    Speeds up queries by allowing fast lookups
- parser
    Converts SQL to AST 
- Engine
    Handles storage and retrieval by executing queries commands
- Storage
    Persists data to disk using a simple file format
- REPL
    Interactive command line interface for testing

### Web application
- API
    RESTful API for database operations
- Web
    Demonstration web application that uses the database for CRUD operations

## Features
Data Types
- INT
- VARCHAR
- BOOLEAN
- DATE
- TIMESTAMP
- FLOAT

Constraints
- Primary Key
- Unique 

SQL-like Operations
- CREATE TABLE
- INSERT
- SELECT
- UPDATE
- DELETE

Query Capabilities
- WHERE (equality only)
- INNER JOIN (equality join)

Indexing
- Hash-map index for primary keys

Interface
- Interactive REPL
- API for web app

## Web Application Demonstration
The web app will demonstrate real usage of the database in a fintech-relevant context.
Example Domain
- Users
- Payments / Transactions
- Merchants (optional)

Features
- Create users
- Record payments
- List payments per user (JOIN)
- CRUD operations backed by the custom RDBMS

### Important:
The web app will use this database engine, not SQLite or another external DB.

## Trade-offs and Transparency
- Hash-map indexes instead of B-trees for simplicity
- Nested-loop joins (O(n × m)) acceptable for small datasets
- No query planner
- Optional or simple persistence (e.g., JSON)

### Use of AI Tools
AI tools may be used for:
- Brainstorming
- Syntax assistance
- Design discussion

All architectural decisions and final implementations are the author’s own.
