from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from movies.models import Filmwork
from movies.models import PersonFilmWork as PF


class MoviesApiMixin(object):
    model = Filmwork
    http_method_names = ["get"]
    pk_url_kwarg = "uuid"

    def get_queryset(self):
        actors = ArrayAgg("persons__full_name", filter=Q(personfilmwork__role=PF.RoleInFilmwork.ACTOR), distinct=True)
        directors = ArrayAgg(
            "persons__full_name",
            filter=Q(personfilmwork__role=PF.RoleInFilmwork.DIRECTOR),
            distinct=True,
        )
        writers = ArrayAgg("persons__full_name", filter=Q(personfilmwork__role=PF.RoleInFilmwork.WRITER), distinct=True)
        genres = ArrayAgg("genres__name", distinct=True)

        return (
            Filmwork.objects.prefetch_related("genres", "person")
            .all()
            .values(
                "id",
                "title",
                "description",
                "creation_date",
                "rating",
                "type",
                "file_path",
            )
            .annotate(
                genres=genres,
                actors=actors,
                directors=directors,
                writers=writers,
            )
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)
