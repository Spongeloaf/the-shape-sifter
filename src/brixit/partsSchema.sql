DROP TABLE IF EXISTS unlabelledParts;

CREATE TABLE unlabelledParts (
    puid   CHAR (12) PRIMARY KEY NOT NULL,
    user   INTEGER NOT NULL,
    images TEXT   NOT NULL
);
