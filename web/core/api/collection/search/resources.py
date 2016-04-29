"""Adding search functionality."""
from django.conf.urls import url
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404

from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from haystack.query import SearchQuerySet
from web.blog.models import Entry


class SearchEntriesResource(ModelResource):
    """docstring for SearchEntriesResource."""

    class Meta:
        """Inner class."""

        queryset = Entry.objects.all()
        resource_name = 'all_entries'

    def prepend_urls(self):
        """Prepend urls."""
        return [
            url(
                r'^(?P<resource_name>{0})/search{1}'.format(self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_search_entries'),
                name='api_get_search_entries')
        ]

    def get_search_entries(self, request, **kwargs):
        """Get search."""
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        sqs = SearchQuerySet().models(Entry).load_all().auto_query(request.GET.get('q', ''))
        paginator = Paginator(sqs, 20)

        try:
            page = paginator.page(int(request.GET.get('page', 1)))
        except InvalidPage:
            raise Http404('Sorry, no results on that page.')

        objects = []

        for result in page.object_list:
            bundle = self.build_bundle(obj=result.object, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)
