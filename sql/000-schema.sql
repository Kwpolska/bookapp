-- Bookapp Migration 000
-- Initial DB schema (v4)

CREATE TABLE Author (
    id SERIAL PRIMARY KEY NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL
);

CREATE TABLE Book (
    id SERIAL PRIMARY KEY NOT NULL,
    title VARCHAR(200) NOT NULL,
    author_id INTEGER REFERENCES authors(id) NOT NULL,
    isbn VARCHAR(17) NULL,
);

CREATE TABLE BookCopy (
    id SERIAL PRIMARY KEY NOT NULL,
    book_id INTEGER REFERENCES books(id) NOT NULL
);

CREATE TABLE Patron (
    id SERIAL PRIMARY KEY NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    rental_limit SMALLINT NOT NULL
);

CREATE TABLE AdminUser (
    id SERIAL PRIMARY KEY NOT NULL,
    firstname VARCHAR(100) NOT NULL,
    lastname VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(120) NOT NULL
);

CREATE TABLE Rental (
    id SERIAL PRIMARY KEY NOT NULL,
    book_copy_id INTEGER REFERENCES book_copies(id) NOT NULL,
    patron_id INTEGER REFERENCES patrons(id) NOT NULL,
    rental_date TIMESTAMP NOT NULL,
    return_by TIMESTAMP NOT NULL,
    returned TIMESTAMP NULL
);
