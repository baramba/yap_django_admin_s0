import random
import uuid
import psycopg2

from datetime import datetime
from faker import Faker
from psycopg2.extras import execute_batch

fake = Faker()

# Подготавливаем DSN (Data Source Name) для подключения к БД Postgres
dsn = {
    "dbname": "movies_db",
    "user": "app",
    "password": "pass",
    "host": "localhost",
    "port": 5432,
    "options": "-c search_path=content",
}

PERSONS_COUNT = 100000
PAGE_SIZE = 5000

now = datetime.utcnow()

# Установим соединение с БД используя контекстный менеджер with.
# В конце блока автоматически закроется курсор (cursor.close())
# и соединение (conn.close())
with psycopg2.connect(**dsn) as conn, conn.cursor() as cur:

    # Заполнение таблицы Person
    persons_ids = [str(uuid.uuid4()) for _ in range(PERSONS_COUNT)]
    query = "INSERT INTO person (id, full_name, created, modified) \
                    VALUES (%s, %s, %s, %s)"
    data = [(pk, fake.last_name(), now, now) for pk in persons_ids]
    execute_batch(cur, query, data, page_size=PAGE_SIZE)
    conn.commit()

    # Заполнение таблицы PersonFilmWork
    person_film_work_data = []
    roles = ["actor", "producer", "director"]

    cur.execute("SELECT id FROM film_work")
    film_works_ids = [data[0] for data in cur.fetchall()]

    for film_work_id in film_works_ids:
        for person_id in random.sample(persons_ids, 5):
            role = random.choice(roles)
            person_film_work_data.append(
                (str(uuid.uuid4()), film_work_id, person_id, role, now)
            )

    query = "INSERT INTO person_film_work (id, film_work_id, person_id, role, created) \
                    VALUES (%s, %s, %s, %s, %s)"
    execute_batch(cur, query, person_film_work_data, page_size=PAGE_SIZE)
    conn.commit()

    # cur = pg_conn.cursor()
    # cur.execute("""TRUNCATE content.genre_film_work CASCADE""")
    # cur.execute("""TRUNCATE content.person_film_work CASCADE""")
    # cur.execute("""TRUNCATE content.genre CASCADE""")
    # cur.execute("""TRUNCATE content.person CASCADE""")
    # cur.execute("""TRUNCATE content.film_work CASCADE""")
    # pg_conn.commit()
    # размер порции записей для переноса = fetch_size * 10

SRC_SCHEMA_DICT = MappingProxyType(
    {
        "film_work": [
            "id",
            "title",
            "description",
            "creation_date",
            "rating",
            "type",
            "created",
            "modified",
            "file_path",
        ],
        "genre": [
            "id",
            "name",
            "description",
            "created",
            "modified",
        ],
        "genre_film_work": [
            "id",
            "genre_id",
            "film_work_id",
            "created",
        ],
        "person": [
            "id",
            "full_name",
            "created",
            "modified",
        ],
        "person_film_work": [
            "id",
            "film_work_id",
            "person_id",
            "role",
            "created",
        ],
    }
)


# детальная информация об ошибке
# err_obj, traceback = sys.exc_info()
# logging.log(err_obj, traceback)
