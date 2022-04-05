#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import datetime
import os
import timeit

import django
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import connection, models, reset_queries
from django.db.models import Count, ExpressionWrapper, F, Q
from django.db.models.functions import Abs, ExtractDay

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


from movies.models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmWork

reset_queries()

# select_related - forieng key
""" filmworks_genres = GenreFilmwork.objects.all().select_related("film_work", "genre")[:3]
for filmwork_genre in filmworks_genres:
    print(filmwork_genre.film_work.title, " - ", filmwork_genre.genre.name)

reset_queries()
 """

# prefetch_related - M2M
""" filmworks = Filmwork.objects.prefetch_related("genres", "persons").filter(
    title__icontains="Star wars"
)[:10]

for filmwork in filmworks:
    print(filmwork.genres.all())
    print(filmwork.persons.all()) """

# prefetch_related + select_related
""" filmworks = (
    Filmwork.objects.prefetch_related("genres", "persons")
    .select_related()
    .filter(title__icontains="Star wars")[:10]
)
for filmwork in filmworks:
    print(filmwork.genres.all())
    print(filmwork.persons.all())
 """

# slices
""" all_genres = Genre.objects.all()
print(all_genres[:5])
print(all_genres[5:10]) """


# Количество запросов можно уменьшить, задействовав prefetch_related
""" star_wars_films = Filmwork.objects.prefetch_related("genres", "persons").filter(
    title__icontains="Star Wars"
)[:10]

for filmwork in star_wars_films:
    print(filmwork.genres.all())
    print(filmwork.persons.filter(full_name="Robert")) """


# Count vs len
""" def a():
    Filmwork.objects.filter(genres__name="Western").count()


def b():
    len(Filmwork.objects.filter(genres__name="Western"))


print(timeit.timeit(a, number=100))
print(timeit.timeit(b, number=100))
 """

# filter-chain
""" films = Filmwork.objects.filter(title__startswith="Star").filter(rating__range=[6, 9]) """


# Q - выражения. Фильтрация с использованием ИЛИ
""" films = Filmwork.objects.filter(
    Q(rating__gte=8, creation_date__gte=datetime.date(year=2020, month=1, day=1))
    | Q(rating=1)
).count() 
"""


# Использование значений полей внутри запроса
""" need_to_increase_rating = Filmwork.objects.filter(persons__full_name="Samuli Torssonen")
for film in need_to_increase_rating:
    print(film.title, film.description, film.rating)

need_to_increase_rating.update(rating=F("rating") + 0.2) """

# Добавление новых полей и расчёты по всему QuerySet
# наивная реализация подсчета
""" actors = Person.objects.filter(
    personfilmwork__role=PersonFilmWork.RoleInWorkfilm.ACTOR
).prefetch_related("filmwork_set")
for actor in actors:
    print(actor.full_name, actor.filmwork_set.count()) """


# то же самое можно сделать всего одним запросом, используя аннотации.
""" print(
    *Person.objects.filter(personfilmwork__role=PersonFilmWork.RoleInWorkfilm.ACTOR)
    .values_list("full_name")
    .annotate(count=Count("filmwork")),
    sep="\n"
)

print(
    Person.objects.filter(personfilmwork__role=PersonFilmWork.RoleInWorkfilm.ACTOR)
    .values("full_name")
    .annotate(count=Count("filmwork"))
)

print(
    Person.objects.filter(
        personfilmwork__role=PersonFilmWork.RoleInWorkfilm.ACTOR
    ).values("full_name")
) """

# Допустим, вы хотите найти фильм, который был выпущен в прокат недалеко от важной для вас даты. Для этого вам нужно рассчитать расстояние между датами используя F, привести результат к количеству дней при помощи ExtractDay, избавится от отрицательных значений при помощи Abs, отсортировать по получившемуся числу и взять первый фильм.

""" filmwork_qs = Filmwork.objects.all()
expr = ExtractDay(
    ExpressionWrapper(
        datetime.datetime(2018, 11, 8) - F("creation_date"),
        output_field=models.DateField(),
    )
)
film = (
    filmwork_qs.annotate(delta=expr)
    .filter(delta__isnull=False)
    .annotate(abs_delta=Abs("delta"))
    .order_by("abs_delta")
    .first()
)
print(film) """

# Агригация
""" Filmwork.objects.filter(persons__full_name='Harrison Ford').aggregate(Avg('rating'))
 """

# RAW sql
""" film = Filmwork.objects.raw(
    'SELECT id, age(creation_date) AS age FROM "content"."film_work"'
)[0]
print(film.title, film.age) """

# Func
""" from django.db.models import F, Func

class SwitchFullname(Func):
    function = 'regexp_replace'  
    template = r'''%(function)s(%(expressions)s, '(\w+)(\W+)(\w+)', '\3\2\1')'''  

Person.objects.update(full_name=SwitchFullname(F('full_name')))

 """


# Для создания группы объектов такой способ будет неэффективен: вам понадобится столько же запросов, сколько записей в вашей группе. Чтобы оптимизировать действия с наборами объектов, в Django реализованы методы bulk_create и bulk_update. Они принимают на вход список экземпляров класса модели.
# По умолчанию все записи создаются одним запросом. Но если вы хотите создать сразу много записей, SQL-запрос получится очень большим. В этом случае вы можете позволить Django разделить его на несколько, указав параметр batch_size.

""" Filmwork.objects.bulk_create(large_filmworks_list, batch_size=500) 

Genre.objects.bulk_create([Genre(name='Science fiction'), Genre(name='Philosophical')])  """

# bulk_update
""" persons_without_birthday = Person.objects.filter(birth_date__isnull=True)

for person in persons_without_birthday:
    person.birth_date = get_birthday(person.full_name)

Person.objects.bulk_update(persons_without_birthday, field=['birth_date'])  """

# Атомарные транзакции (django.db.transaction.atomic)
""" 
import random 

from django.db import transaction

def get_rating_from_imdb(filmname):
    rating = random.randint(0,6)
    if rating == 6:
        raise Exception("👿")
    return rating
        
# Открытие новой транзакции
@transaction.atomic
def create_film_pack(filmname):
    # Начало транзакции
    # Падение любого участка кода приведёт к откату изменений 
    add_film(filmname)
    add_actors(filmname)
    get_rating_from_imdb(filmname)
    add_genres(filmname)
    # Если блок завершился успешно, произойдёт коммит транзакции  """

# Блокировка записей
# https://postgrespro.ru/docs/postgresql/12/sql-select#SQL-FOR-UPDATE-SHARE

""" persons_without_birthday = Person.objects.select_for_update().filter(birth_date__isnull=True)  # Создание ленивого QuerySet
with transaction.atomic():  # Начало транзакции
    for person in persons_without_birthday:  # Выполнение QuerySet: выполнена блокировка строк на уровне БД
        person.birth_date = get_birthday(person.full_name) 
    ...

# После завершения транзакции блокировка будет снята  """

# Если в запросе с select_for_update указан select_related, Django по умолчанию пытается заблокировать все полученные таблицы. Чтобы этого не происходило, используйте параметр of, в котором можно перечислить только таблицы, требующие блокировки.

""" genres = GenreFilmWork.objects.select_for_update(of=('self',)).select_related('filmwork').filter(filmwork__title='Pop Star on Ice')
with transaction.atomic():
    for person in persons_without_birthday:
        person.birth_date = get_birthday(person.full_name) """

# Запуск при успешном завершении транзакции (transaction.on_commit)

""" from django.db import transaction

with transaction.atomic():
    user = create_user()
    create_profile(user)
    add_random_profile_photo(user)
    transaction.on_commit(
        lambda: set_task_for_send_email_congratulations(user) 
    )  """


# # получить все фильмы
# films = Filmwork.objects.prefetch_related("genres", "persons")[:5]
# for film in films:
#     actors = film.persons.all()
#     print(actors)


# получить все фильмы

""" films = (
    Filmwork.objects.prefetch_related("genres", "person").values().all().annotate(genres=ArrayAgg("genres__name"))[:5]
)
print(films) """

from movies.models import PersonFilmWork as PF

actors = ArrayAgg("persons__full_name", filter=Q(personfilmwork__role=PF.RoleInFilmwork.ACTOR), distinct=True)
directors = ArrayAgg(
    "persons__full_name",
    filter=Q(personfilmwork__role=PF.RoleInFilmwork.DIRECTOR),
    distinct=True,
)
writers = ArrayAgg("persons__full_name", filter=Q(personfilmwork__role=PF.RoleInFilmwork.WRITER), distinct=True)
genres = ArrayAgg("genres__name", distinct=True)
films = (
    Filmwork.objects.prefetch_related("genres", "person")
    .all()
    .values()
    .annotate(
        genres=genres,
        actors=actors,
        directors=directors,
        writers=writers,
    )
)
print(films.get(id="00af52ec-9345-4d66-adbe-50eb917f463a"))

print("\n", connection.queries)
print(len(connection.queries))


# "some_field"
# "-some_field"
# from django.db.models import F

# print(F("-some_field").desc())

""" from django.utils.decorators import classonlymethod


class A:
    a = 1

    def __init__(self) -> None:
        self.a = 10
        self.b = 2

    def getA(self):
        return self.a

    @classonlymethod
    def as_view(cls, **initkwargs):
        print("Привет")


def simpleF(arg1):
    print("я печатаю -", arg1)


def simpleD(func):
    def func_wrapper():
        print("Начало врапера")
        func()
        print("Конец врапера")

    return func_wrapper """


# simpleF = simpleD(simpleF("a"))
# simpleF()

""" 
def a(a):
    def b(b):
        print(a * b)

    return b


f10 = a(10)
f10(5)

f20 = a(10)(5)
 """
