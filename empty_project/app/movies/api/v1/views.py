from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView

from movies.models import Filmwork, PersonFilmwork


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    @staticmethod
    def _arrayagg_person(roletype):
        return ArrayAgg(
            'person__full_name',
            filter=Q(personfilmwork__role__icontains=
                     roletype),
            distinct=True
        )

    def get_queryset(self):
        qrset = self.model.objects.prefetch_related('genres', 'person') \
            .values('id', 'title', 'description', 'creation_date', 'rating', 'type'). \
            all().annotate(genres=ArrayAgg('genres__name',
                                                     distinct=True),
                                     actors=self._arrayagg_person(PersonFilmwork.RoleType.actor),
                                     directors=self._arrayagg_person(PersonFilmwork.RoleType.director),
                                     writers=self._arrayagg_person(PersonFilmwork.RoleType.writer)
                                     )
        return qrset

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.paginate_by
        )
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(paginator.page(page.number)),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        return self.get_object()