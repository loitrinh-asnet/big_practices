"""Entry Resource."""
from django.conf.urls import url
from tastypie import fields
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication
from tastypie.serializers import Serializer
from web.users.models import User
from web.blog.models import Entry
from web.blog.forms import EntryForm
from core.api.collection.users.resources import UserProfileResource
from core.api.validations import EntryValidation
from core.api.authorizations import CustomAuthorization
from core.api.paginators import EntryPaginator
from tastypie.utils import trailing_slash


class EntryResource(ModelResource):
    """docstring for EntryResource."""

    user = fields.ForeignKey(UserProfileResource, 'created_by')

    class Meta:
        """Meta."""

        queryset = Entry.objects.all()
        resource_name = 'entry'
        authentication = BasicAuthentication()
        authorization = CustomAuthorization()
        validation = EntryValidation(form_class=EntryForm)
        list_allowed_methods = ['get']
        details_allowed_methods = ['get', 'put', 'delete']
        serializer = Serializer(['json'])
        paginator_class = EntryPaginator
        filtering = {
            'user': ALL_WITH_RELATIONS,
            'published_date': ['exact', 'lt', 'lte', 'gte', 'gt'],
        }

    def prepend_urls(self):
        """Adding custom endpoints or overriding the buil-in ones."""
        return [
            url(
                r'^(?P<resource_name>{0})/search{1}$'.format(
                    self._meta.resource_name,
                    trailing_slash()),
                self.wrap_view('get_search'),
                name='entry_get_search'
            ),
        ]


class EntryAuthorResource(ModelResource):
    """Entry Author Resource.

    list:
    *example: http://192.168.99.101:8000/api/v1/entry-author/admin
    """

    def prepend_urls(self):
        """
        Adding custom endpoints or overriding the built-in ones.

        Allowing you to define additional URLs by which this resource can be accessed.
        """
        return [
            url(
                r"^(?P<resource_name>%s)/(?P<username>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('get_entry_list'),
                name="entry-author"
            ),
        ]

    def get_entry_list(self, request, **kwargs):
        """
        View function.

        This is the actual view which shows the realted entries.
        It confirms that the client is performing a GET request
        Return the realted entry resources.
        """
        self.method_check(request, ['get'])
        user = User.objects.get(username=kwargs['username'])
        return EntryResource().get_list(request, user=user)

    class Meta:
        """META."""

        resource_name = 'entry-author'
        authentication = BasicAuthentication()
