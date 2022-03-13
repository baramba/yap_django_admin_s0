CREATE SCHEMA IF NOT EXISTS content;

-- Раскомментировать для пересоздания таблиц и индексов

-- DROP TABLE IF EXISTS content.person CASCADE;
-- DROP TABLE IF EXISTS content.person_film_work CASCADE;
-- DROP TABLE IF EXISTS content.genre CASCADE;
-- DROP TABLE IF EXISTS content.genre_film_work CASCADE;
-- DROP TABLE IF EXISTS content.film_work CASCADE;
-- DROP TABLE IF EXISTS content.person CASCADE;

-- DROP INDEX IF EXISTS film_work_person_idx CASCADE;
-- DROP INDEX IF EXISTS film_work_genre_idx CASCADE;


CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL REFERENCES content.film_work,
    person_id uuid NOT NULL REFERENCES content.person,
    role TEXT NOT NULL,
    created timestamp with time zone
); 

CREATE UNIQUE INDEX person_film_work_role_idx ON content.person_film_work (film_work_id, person_id, role);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
); 

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid NOT NULL REFERENCES content.genre,
    film_work_id uuid NOT NULL REFERENCES content.film_work,
    created timestamp with time zone
); 

CREATE UNIQUE INDEX film_work_genre_idx ON content.genre_film_work (film_work_id, genre_id);

