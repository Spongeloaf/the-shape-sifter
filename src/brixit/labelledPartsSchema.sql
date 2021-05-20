DROP TABLE IF EXISTS labelledParts;

CREATE TABLE labelledParts (
    puid   CHAR (12) PRIMARY KEY
                     NOT NULL,
    user   INTEGER   NOT NULL,
    bounty INTEGER   NOT NULL
);