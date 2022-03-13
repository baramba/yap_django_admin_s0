"""Описание основных структур для перноса данных из SQLite в Postgres."""

import uuid
from dataclasses import asdict, astuple, dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import Literal


@dataclass
class _MetaMixin(object):
    """MetaMixin добавляет методы для получения мета информации таблице."""

    _table_name: str = field(default="", repr=False)

    def table_name(self):
        """table_name возвращает название таблицы.

        Returns:
            название таблицы
        """
        return self._table_name

    def get_fields(self):
        """get_fields возвращает список полей дата-класса.

        Returns:
            (list) список полей дата-класса
        """
        fields = list(asdict(self).keys())
        fields.remove("_table_name")

        return fields

    def get_as_tuple(self):
        # Удаляем название таблицы из списка
        rec_values = list(astuple(self))
        rec_values.pop(0)
        return tuple(rec_values)


@dataclass
class _TimeStampMixin(object):
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)


@dataclass
class _UUIDMixin(object):
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Genre(_UUIDMixin, _TimeStampMixin, _MetaMixin):
    """Класс для хранения данных из таблицы Genre."""

    name: str = ""
    description: str = ""
    _table_name: str = "genre"

    def __post_init__(self):
        if self.description is None:
            self.description = ""


@dataclass
class Filmwork(_UUIDMixin, _TimeStampMixin, _MetaMixin):
    """Класс для хранения данных из таблицы Filmwork."""

    title: str = ""
    description: str = ""
    creation_date: datetime = field(default_factory=datetime.now().date)
    rating: float = field(default=float(0))
    type: Literal["movie", "tv_show"] = "movie"
    file_path: str = ""
    _table_name: str = "film_work"

    def __post_init__(self):
        if self.description is None:
            self.description = ""


@dataclass
class Person(_UUIDMixin, _TimeStampMixin, _MetaMixin):
    """Класс для хранения данных из таблицы Person."""

    full_name: str = ""
    _table_name: str = "person"


@dataclass
class GenreFilmwork(_UUIDMixin, _MetaMixin):
    """Класс для хранения данных из таблицы GenreFilmwork."""

    genre_id: uuid.UUID = field(default_factory=uuid.uuid4)
    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)
    created: datetime = field(default_factory=datetime.now)
    _table_name: str = "genre_film_work"


@dataclass
class PersonFilmWork(_UUIDMixin, _MetaMixin):
    """Класс для хранения данных из таблицы PersonFilmWork."""

    film_work_id: uuid.UUID = field(default_factory=uuid.uuid4)
    person_id: uuid.UUID = field(default_factory=uuid.uuid4)
    role: str = ""
    created: datetime = field(default_factory=datetime.now)
    _table_name: str = "person_film_work"


TABLES = (
    Filmwork,
    Person,
    Genre,
    GenreFilmwork,
    PersonFilmWork,
)
