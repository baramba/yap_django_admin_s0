CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.temp_table (id uuid PRIMARY KEY, name TEXT);

INSERT INTO
    content.temp_table (id, name)
VALUES
    (
        'ca211dbc-a6c6-44a5-b238-39fa16bbfe6c',
        'Иван Иванов'
    );

INSERT INTO
    content.temp_table (id, name)
VALUES
    (
        'b8531efb-c49d-4111-803f-725c3abc0f5e',
        'Иван Иванов'
    ) ON CONFLICT (id) DO NOTHING;

INSERT INTO content.temp_table (id, name)
VALUES ('b8531efb-c49d-4111-803f-725c3abc0f5e', 'Иван Иванов')
ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name; 

SELECT * from content.temp_table;

TRUNCATE content.temp_table; 

-- UPSERT

INSERT INTO content.temp_table (id, name)
VALUES ('b8531efb-c49d-4111-803f-725c3abc0f5e', 'Иван Иванов')
ON CONFLICT (id) DO NOTHING; 

INSERT INTO content.temp_table (id, name)
VALUES ('b8531efb-c49d-4111-803f-725c3abc0f5e', 'Иван Иванов')
ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name; \

--  prepare
PREPARE temp_table_insert (uuid, text) AS
    INSERT INTO content.temp_table VALUES($1, $2);

TRUNCATE content.temp_table;
\set autocommit off

BEGIN;
EXECUTE temp_table_insert('ca211dbc-a6c6-44a5-b238-39fa16bbfe6c', 'Иван Иванов');
EXECUTE temp_table_insert('b8531efb-c49d-4111-803f-725c3abc0f5e', 'Василий Васильевич');
EXECUTE temp_table_insert('2d5c50d0-0bb4-480c-beab-ded6d0760269', 'Пётр Петрович');
COMMIT;

\set autocommit on 

