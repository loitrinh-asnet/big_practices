"""Public."""
from django.conf.urls import url
from . import views

urlpatterns = [
    # URL pattern for the IndexView
    url(
        regex=r'^$',
        view=views.IndexView.as_view(),
        name='entry_index'
    ),
    # URL pattern for the DetailsView
    url(
        regex=r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        view=views.DetailsView.as_view(),
        name='entry_details'
    ),
    # URL pattern for create new entry
    url(
        regex=r'^entry/new/$',
        view=views.CreateEntryView.as_view(),
        name='entry_new',
    ),
    # URL pattern for InstallBlog
    url(
        regex=r'^install',
        view=views.InstallBlog.as_view(),
        name='blog_install',
    ),
    # URL pattern for Create Blog
    url(
        regex=r'^create',
        view=views.CreateBlog.as_view(),
        name='blog_create',
    ),
    # URL pattern for update Blog
    url(
        regex=r'^update/(?P<pk>\d+)/$',
        view=views.UpdateBlog.as_view(),
        name='blog_update',
    ),
    # URL pattern for DetailsBlog
    url(
        regex=r'^details/(?P<pk>\d+)/$',
        view=views.DetailsBlog.as_view(),
        name='blog_details',
    ),
    # URL pattern for Author
    url(
        regex=r'author/(?P<username>[\w.@+-]+)/$',
        view=views.AuthorView.as_view(),
        name='author',
    ),

    # URL pattern for Search
    url(
        regex=r'^search/',
        view=views.entry_search,
        name='entry_search'
    ),
]
