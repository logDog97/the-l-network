DROP TABLE IF EXISTS users;
CREATE TABLE users(
    uName TEXT PRIMARY KEY,
    realName TEXT NOT NULL,
    gender TEXT NOT NULL,
    userPass TEXT NOT NULL
);

