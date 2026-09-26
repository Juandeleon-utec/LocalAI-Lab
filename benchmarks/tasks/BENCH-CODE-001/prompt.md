# BENCH-CODE-001 v1.0 — Participant Prompt

Develop a complete, functional web application using Node.js and MySQL.

Work only inside the repository provided to you. You may create, modify and delete files inside that repository as required by the task.

## Objective

Implement a small authenticated application that allows users to register, log in and manage records that belong only to them.

The finished application must include:

- a Node.js backend;
- a MySQL database;
- a REST API;
- a minimal functional web frontend;
- setup and execution documentation.

Do not store passwords in plain text.

## Data model

Use two principal database tables.

### `users`

Must contain at least:

- `id`: unique identifier;
- `username`: unique user name;
- `password_hash`: securely hashed password;
- `created_at`: creation timestamp.

### `records`

Must contain at least:

- `id`: unique identifier;
- `user_id`: owner of the record;
- `title`: record title;
- `value`: text value/content;
- `created_at`: creation timestamp;
- `updated_at`: last-modification timestamp.

`records.user_id` must have referential integrity with `users.id`.

## Required REST API contract

Implement these endpoints exactly:

### Health

`GET /health`

- return HTTP 200 when the application and database connection are ready;
- return JSON containing `{"status":"ok"}`.

### Authentication

`POST /api/auth/register`

Request JSON:

```json
{
  "username": "example",
  "password": "example-password"
}
```

Expected behavior:

- HTTP 201 for successful registration;
- HTTP 400 for invalid input;
- HTTP 409 if the username already exists.

`POST /api/auth/login`

Request JSON uses the same `username` and `password` fields.

Expected behavior:

- HTTP 200 for valid credentials;
- HTTP 401 for invalid credentials;
- successful login must return a bearer authentication token in the JSON field `token`.

Protected API requests must accept:

```text
Authorization: Bearer <token>
```

### Records

All record endpoints require authentication.

`GET /api/records`

Return only records owned by the authenticated user.

`POST /api/records`

Request JSON:

```json
{
  "title": "Example title",
  "value": "Example value"
}
```

Create a record owned by the authenticated user.

`GET /api/records/:id`

Return the specified record only when it belongs to the authenticated user.

`PUT /api/records/:id`

Allow the owner to update `title` and/or `value`.

`DELETE /api/records/:id`

Allow the owner to delete the record.

A user must never be able to read, update or delete another user's records.

Use suitable HTTP status codes. In particular:

- 400 for invalid input;
- 401 when authentication is missing or invalid;
- 403 or 404 when an authenticated user attempts to access another user's record;
- 404 for nonexistent resources;
- 409 for duplicate usernames;
- 500 only for unexpected server failures.

## Web frontend

Provide a minimal functional web interface.

It must expose these browser routes:

- `/register`;
- `/login`;
- `/app`.

The interface must allow a user to:

1. register;
2. log in;
3. log out;
4. view their records;
5. create a record;
6. edit a record;
7. delete a record.

The frontend does not need elaborate visual design. Prioritize correctness, usability, clarity and maintainability.

## Configuration

Read configuration from environment variables.

Support at least:

- `PORT`;
- `DB_HOST`;
- `DB_PORT`;
- `DB_NAME`;
- `DB_USER`;
- `DB_PASSWORD`;
- `AUTH_SECRET`.

Provide a `.env.example` containing variable names and safe example values but no real credentials.

Do not commit secrets.

## Database initialization

Provide a reproducible way to create the required schema on a clean MySQL database.

It may be a migration, initialization script, application startup mechanism or another documented approach.

Do not require manual SQL editing after the project has been delivered.

## Security and validation

The implementation must:

- hash passwords with a password-hashing mechanism appropriate for authentication;
- never store the original password;
- validate incoming data;
- use parameterized queries or an equivalent mechanism that prevents SQL injection;
- enforce record ownership on the server, not only in the frontend;
- avoid secrets in source code.

Choose libraries and internal architecture yourself. Do not select packages merely to minimize the number of files or lines.

## Code quality

Organize the code in a reasonable, maintainable structure.

Avoid both unnecessary complexity and excessive code compression.

Prioritize:

- clear naming;
- separation of responsibilities;
- readable functions;
- maintainable modules;
- minimal duplication;
- useful error handling.

Do not place the entire application in one file if separating responsibilities would materially improve maintainability.

## Required commands

The finished repository must support:

```bash
npm install
npm start
```

Document any additional initialization command in `README.md`.

## Verification requirement

Do not consider the task complete merely because files were generated.

Before finishing:

1. install required dependencies;
2. initialize the database schema;
3. start the application;
4. verify `GET /health`;
5. test registration;
6. test login;
7. test creation of a record;
8. test listing and retrieval;
9. test modification;
10. test deletion;
11. create a second user and verify that one user cannot access the other's records;
12. correct any errors found;
13. rerun failed checks after each correction.

Continue the edit -> execute -> diagnose -> fix -> retest loop until the application works or you reach an unrecoverable limitation.

## Final report

At the end, report:

- files created or modified;
- application structure;
- authentication approach;
- password-storage approach;
- database initialization approach;
- verification commands actually executed;
- errors encountered and corrected;
- any remaining limitation.

Do not claim that a check passed unless you actually executed it.
