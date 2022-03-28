from asyncio.log import logger
from csv import writer
from multiprocessing import context

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.api.v1.base import MoviesApiMixin
from movies.models import Filmwork
from movies.models import PersonFilmWork as PF


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        paginator, page, _, _ = self.paginate_queryset(self.get_queryset(), self.paginate_by)
        return {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            "results": list(page.object_list),
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, *, object_list=None, **kwargs):
        return kwargs.get("object")
