SELECT * FROM "content"."film_work" LIMIT 10;


INSERT INTO content.film_work (id, title, type, creation_date, rating) SELECT uuid_generate_v4(), 'some name', case when RANDOM() < 0.3 THEN 'movie' ELSE 'tv_show' END , date::DATE, floor(random() * 100)
FROM generate_series(
  '1900-01-01'::DATE,
  '2021-01-01'::DATE,
  '1 hour'::interval
) date; 



\timing on 

Скопируем текущую таблицу в csv-файл. /output.csv — путь до файла, куда будут записаны данные таблицы. Вы можете указать любой удобный путь.
\copy (select * from content.film_work) to '/home/babikhin/project/yandex/new_admin_panel_sprint_1/01_schema_design/other/output.csv' with csv 

Удалим данные из таблицы.
TRUNCATE content.film_work; 

Удалим индекс.
DROP INDEX content.film_work_creation_date_idx; 

Скопируем данные из файла в таблицу /output.csv замените на путь из операции сохранения данных.
\copy content.film_work from '/home/babikhin/project/yandex/new_admin_panel_sprint_1/01_schema_design/other/output.csv' with NULL '' delimiter ','; 

Снова удалим данные из таблицы.
TRUNCATE content.film_work; 

Вернём индекс на место.
CREATE INDEX film_work_creation_date_idx ON content.film_work(creation_date); 

Заново скопируем данные.
\copy content.film_work from '/home/babikhin/project/yandex/new_admin_panel_sprint_1/01_schema_design/other/output.csv' with NULL '' delimiter ','; 