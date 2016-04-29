"""Provides URLconf details for the Api."""
from django.conf.urls import url, include
from tastypie.api import Api
from .collection.users.resources import UserProfileResource, CreateUserResource, UserResource
from .collection.entries.resources import EntryResource, EntryAuthorResource
from .collection.search.resources import SearchEntriesResource

# API definition
v1_api = Api(api_name='v1')

# Register an instance of all neccessary Resources
v1_api.register(UserProfileResource())
v1_api.register(CreateUserResource())
v1_api.register(EntryAuthorResource())
v1_api.register(EntryResource())
v1_api.register(UserResource())
v1_api.register(SearchEntriesResource())

# Standard bits
urlpatterns = [
    url(r'^', include(v1_api.urls)),
]

# # Enable documentation for an api endpoint by adding a URL to your urlpatterns
urlpatterns += [
    url(
        r'documentations',
        include('tastypie_swagger.urls', namespace='api_tastypie_swagger'),
        kwargs={
            # Either your tastypie api instance or a string containing the full path to your tastypie api instance
            'tastypie_api_module': v1_api,
            'namespace': 'api_tastypie_swagger',
            'version': '0.1',
        }
    )
]
