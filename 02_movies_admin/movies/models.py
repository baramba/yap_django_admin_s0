import uuid

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    # auto_now_add автоматически выставит дату создания записи
    created = models.DateTimeField(_("created"), auto_now_add=True)
    # auto_now изменятся при каждом обновлении записи
    modified = models.DateTimeField(_("modified"), auto_now=True)

    class Meta:
        # Этот параметр указывает Django, что этот класс не является представлением таблицы
        abstract = True


class UUIDMixin(models.Model):
    # Типичная модель в Django использует число в качестве id. В таких ситуациях поле не описывается в модели.
    # Вам же придётся явно объявить primary key.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    """Жанры."""

    # Первым аргументом обычно идёт человекочитаемое название поля
    name = models.CharField(_("name"), max_length=150)
    # blank=True делает поле необязательным для заполнения.
    description = models.TextField(_("description"), blank=True, max_length=350)

    class Meta:
        # Ваши таблицы находятся в нестандартной схеме. Это нужно указать в классе модели
        db_table = 'content"."genre'
        # Следующие два поля отвечают за название модели в интерфейсе
        verbose_name = _("Genre_verbose_name")
        verbose_name_plural = _("Genre__verbose_name_plural")

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    """Участник кинопроизведения."""

    full_name = models.CharField(_("person_full_name"), max_length=200, blank=False)

    class Meta:
        db_table = 'content"."person'
        verbose_name = _("Person_verbose_name")
        verbose_name_plural = _("Person_verbose_name_plural")

    def __str__(self):
        return self.full_name


class Filmwork(TimeStampedMixin, UUIDMixin):
    """Кинопроизведения."""

    # Название
    title = models.CharField(_("title"), max_length=150)
    # Описание
    description = models.TextField(_("description"), blank=True, max_length=350)
    # Дата выхода
    creation_date = models.DateField(_("creation_date"), blank=False)
    # Рейтинг
    rating = models.FloatField(
        _("rating"),
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    # Тип кинопроизведения
    class FilmType(models.TextChoices):
        MOVIE = "movie", _("movie")
        TV_SHOW = "tv_show", _("tv_show")

    type = models.CharField(_("type"), max_length=10, choices=FilmType.choices)

    # Жанры
    genres = models.ManyToManyField(
        Genre,
        through="GenreFilmwork",
        verbose_name=_("Genre_verbose_name"),
    )
    # Участники
    persons = models.ManyToManyField(
        Person,
        through="PersonFilmWork",
        verbose_name=_("Person_verbose_name"),
    )
    # Путь к файлу
    file_path = models.FileField(_("file_field"), blank=True, null=True, upload_to=None)

    class Meta:
        # Ваши таблицы находятся в нестандартной схеме. Это нужно указать в классе модели
        db_table = 'content"."film_work'
        # Следующие два поля отвечают за название модели в интерфейсе
        verbose_name = _("Filmwork_verbose_name")
        verbose_name_plural = _("Filmwork_verbose_name_plural")

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    """Связь кинопроизведений и жанров"""

    genre = models.ForeignKey("Genre", on_delete=models.CASCADE)
    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        verbose_name = _("GenreFilmwork_verbose_name")
        verbose_name_plural = _("GenreFilmwork_verbose_name_plural")


class PersonFilmWork(UUIDMixin):
    """Связь кинопроизведения с участником."""

    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    role = models.CharField(_("role"), blank=False, max_length=150)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        verbose_name = _("PersonFilmWork_verbose_name")
        verbose_name_plural = _("PersonFilmWork_verbose_name_plural")
