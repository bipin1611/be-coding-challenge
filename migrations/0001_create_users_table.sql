CREATE TABLE IF NOT EXISTS users (
    id            SERIAL          PRIMARY KEY,
    system        VARCHAR(100)    NOT NULL,
    username      VARCHAR(255)    NOT NULL,
    password      VARCHAR(255)    NOT NULL,
    name          VARCHAR(255)    NULL,
    email         VARCHAR(255)    NULL,
    created_at    TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email    UNIQUE (email)
);

CREATE INDEX IF NOT EXISTS ix_users_username ON users (username);
CREATE INDEX IF NOT EXISTS ix_users_system ON users (system);
CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);
