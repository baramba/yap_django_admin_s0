import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(_("created"), auto_now_add=True)
    modified = models.DateTimeField(_("modified"), auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    """Жанры."""

    name = models.CharField(_("name"), max_length=150)
    description = models.TextField(_("description"), blank=True, max_length=350)

    class Meta:
        db_table = 'content"."genre'
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
    creation_date = models.DateField(_("creation_date"), blank=False, null=True)
    # Рейтинг
    rating = models.FloatField(
        _("rating"),
        blank=True,
        null=True,
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
        db_table = 'content"."film_work'
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
        indexes = [models.Index(fields=["film_work", "genre"], name="film_work_genre_idx")]


class PersonFilmWork(UUIDMixin):
    """Связь кинопроизведения с участником."""

    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)

    # Роль участника в кинопроизведении
    class RoleInFilmwork(models.TextChoices):
        ACTOR = "actor", _("actor")
        DIRECTOR = "director", _("director")
        WRITER = "writer", _("writer")

    role = models.CharField(
        _("role"),
        choices=RoleInFilmwork.choices,
        blank=False,
        max_length=10,
    )

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        verbose_name = _("PersonFilmWork_verbose_name")
        verbose_name_plural = _("PersonFilmWork_verbose_name_plural")

        indexes = [models.Index(fields=["film_work", "person", "role"], name="person_film_work_role_idx")]
