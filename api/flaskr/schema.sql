DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS contract;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    mailbox VARCHAR(255),
    phone INT(10),
    idContract INT,
    activate BOOLEAN
);

CREATE TABLE contract (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idUser INT,
    name VARCHAR(255) NOT NULL,
    date_issued TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    date_expires DATE NOT NULL,
    nb_kids INT,
    activate BOOLEAN,
    FOREIGN KEY (idUser) REFERENCES user (id)
);

CREATE TABLE contract_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idContract INT,
    FOREIGN KEY (idContract) REFERENCES contract (id)
);