from django.contrib import admin


from .models import Filmwork
from .models import Genre
from .models import GenreFilmwork
from .models import Person
from .models import PersonFilmWork

# Register your models here.


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "created",
        "modified",
    )


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmWork


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (
        GenreFilmworkInline,
        PersonFilmworkInline,
    )
    # Отображение полей в списке
    list_display = (
        "title",
        "type",
        "creation_date",
        "rating",
    )
    # Фильтрация в списке
    list_filter = ("type", "genres")
    # Поиск по полям
    search_fields = ("title", "description", "id")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "created",
        "modified",
    )
    search_fields = ("full_name",)
