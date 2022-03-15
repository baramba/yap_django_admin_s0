from datetime import datetime
from os import XATTR_CREATE
from re import X
from typing import List
import uuid
from dataclasses import dataclass, field


@dataclass
class Movie:
    title: str
    description: str
    rating: float = field(default=0.0)
    id: uuid.UUID = field(default_factory=uuid.uuid4)


movie = Movie(title="movie", description="new movie", rating=0.0)


print(movie)

Movie(
    title="movie",
    description="new movie",
    rating=0.0,
    id=uuid.UUID("6fe77164-1dfe-470d-a32d-071973759539"),
)


@dataclass
class C:
    mylist: list[int] = field(default_factory=list)


c = C()
c.mylist += [1, 2, 3]

src_db = {
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


a = list()
print(a)
d = datetime.now()
u = uuid.UUID("6fe77164-1dfe-470d-a32d-071973759539")



        # for table_name, columns_name in SRC_SCHEMA_DICT.items():
        #     rows_data = []
        #     columns = ",".join(columns_name)
        #     # Приведение названий полей к названиям в SQLite
        #     columns = columns.replace("created", "created_at")
        #     columns = columns.replace("modified", "updated_at")
        #     sql_text = "select {columns} from {table_name}".format(
        #         columns=columns,
        #         table_name=table_name,
        #     )

        #     for row in self.get_row_gen(sql_text):
        #         rows_data.append(row)
        #     movies_data[table_name] = rows_data


