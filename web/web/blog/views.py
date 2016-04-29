"""Public."""
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.http import HttpResponseRedirect, Http404
from django.views.generic import ListView, DetailView, TemplateView, FormView, CreateView, UpdateView
from django.core.urlresolvers import reverse, reverse_lazy
from datetime import datetime
from web.users.models import User
from . import utils
from . import mixins
from .models import Blog, Entry, Comment
from .forms import BlogForm, EntryForm, CommentForm, SearchForm
from haystack.query import SearchQuerySet
from haystack.utils import Highlighter


# BEST PRACTICES CBVS
# Using mixins withs CBVs
# A mixin is a class that provides functionality to be inhirited
# Can be used to add enhanced functionality and behavior to classses


class InstallBlog(mixins.LoginRequireMixin, TemplateView):
    """Install blog."""

    template_name = 'blog/install.html'

    def get(self, request, *args, **kwargs):
        """Docstring."""
        if utils.is_blog_installed():
            return HttpResponseRedirect(reverse('blog:entry_index'))
        return super(InstallBlog, self).get(request, *args, **kwargs)


class CreateBlog(mixins.AdminRequireMixin, mixins.BlogActionMixin, CreateView):
    """Creating new blog."""

    success_msg = "created"
    form_class = BlogForm
    required_permissions = ('blog | blog | Can add blog')

    def get(self, request, *args, **kwargs):
        """Docstring."""
        blog = Blog.objects.get_blog()
        if blog:
            return HttpResponseRedirect(reverse('blog:blog_details', kwargs={'pk': blog.id}))
        return super(CreateBlog, self).get(request, *args, **kwargs)


class UpdateBlog(mixins.LoginRequireMixin, mixins.PermissionsRequiredMixin, mixins.BlogActionMixin, UpdateView):
    """Updating existing blog."""

    success_msg = "updated"
    form_class = BlogForm
    required_permissions = ('blog.update_blog')


class DetailsBlog(mixins.LoginRequireMixin, mixins.PermissionsRequiredMixin, DetailView):
    """Details of Blog."""

    model = Blog
    required_permissions = ('blog.view_blog')


class IndexView(ListView):
    """Subclassing generic views."""

    # Overriding the default template
    template_name = 'blog/index.html'

    # Making 'friendly' template context
    context_object_name = 'entries'

    def get(self, request, *args, **kwargs):
        """Docstring."""
        blog = Blog.objects.get_blog()

        if not blog:
            return HttpResponseRedirect(reverse('blog:blog_install'))

        if not self.get_queryset():
            return HttpResponseRedirect(reverse('blog:entry_new'))

        self.kwargs['blog'] = blog
        return super(IndexView, self).get(request, *args, **kwargs)

    def get_paginate_by(self, queryset):
        """Docstring."""
        paginate_by = self.kwargs['blog'].entries_per_page
        return paginate_by

    def get_context_data(self, **kwargs):
        """Docstring."""
        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)

        # Maybe adding extra context

        # return new context data
        return context

    def get_queryset(self):
        """Docstring."""

        self.entries = Entry.objects.all()
        return self.entries


class CreateEntryView(mixins.AdminRequireMixin, mixins.EntryActionMixin, CreateView):
    """docstring for Create."""

    success_msg = "Entry was created"
    form_class = EntryForm

    def get_initial(self):
        """Get initial."""
        initial_data = super(CreateEntryView, self).get_initial()
        data_plus = {
            'blog': Blog.objects.get(author=self.request.user),
            'created_by': self.request.user.id,
            'published_date': datetime.now()}
        initial_data.update(data_plus)

        return initial_data


class DetailsView(DetailView):
    """Provides the entry to the context."""

    context_object_name = 'entry'

    def get(self, request, *args, **kwargs):
        """."""
        if not Blog.objects.get_blog():
            return HttpResponseRedirect(reverse('blog_install'))
        return super(DetailsView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """The default implementation simply adds the object being displayed to the template."""
        #  Call the base implementation first to get a context
        context = super(DetailsView, self).get_context_data(**kwargs)

        # Adding extra context
        init_data = {}
        if self.request.user.is_authenticated():
            init_data['name'] = self.request.user.get_full_name() or self.request.user.username
            init_data['email'] = self.request.user.email
        else:
            init_data['name'] = self.request.session.get("name", "")
            init_data['email'] = self.request.session.get("email", "")
        init_data['url'] = self.request.session.get("url", "")

        entry = context['entry']
        comment_form = CommentForm(initial=init_data)
        comments = Comment.objects.filter(entry=entry, is_spam=False)
        context.update({'comments': comments, 'comment_form': comment_form})
        return context

    def get_object(self):
        """Get object."""
        if 'year' and 'month' and 'day' and 'slug' in self.kwargs:
            print(self.kwargs['month'])
            try:
                entry = Entry.default.get(
                    created_date__year=self.kwargs['year'],
                    created_date__month=self.kwargs['month'],
                    created_date__day=self.kwargs['day'],
                    slug=self.kwargs['slug'])

            except Entry.DoesNotExist:
                raise Http404
            except Entry.MultipleObjectsReturned:
                raise Http404
        else:
            raise Http404

        if not entry.is_published:
            raise Http404
        return entry

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        print(context)
        comment_form = CommentForm(self.request.POST)

        if comment_form.is_valid():

            commentter = self.request.user if self.request.user.is_authenticated() else None

            comment = Comment(
                text=comment_form.cleaned_data['text'],
                create_by=commentter,
                entry=self.object,
                user_name=comment_form.cleaned_data['name'],
                user_url=comment_form.cleaned_data['url'])

            comment.is_public = True
            comment.is_spam = False
            if not comment.is_spam:
                self.request.session['user'] = comment_form.cleaned_data['name']
                self.request.session['email'] = comment_form.cleaned_data['email']
                self.request.session['url'] = comment_form.cleaned_data['url']
            comment.save()
            return HttpResponseRedirect('#comment-%s' % comment.pk)
        context.update({'comment_form': comment_form})
        return self.render(context)


class AuthorView(ListView):
    """docstring for Aut"""

    template_name = 'blog/author.html'
    context_object_name = 'entries'

    def get_queryset(self):
        author = get_object_or_404(User, username=self.kwargs['username'])
        self.kwargs['author'] = author
        author_entries = author.entry_set.filter(is_published=True)
        return author_entries

    def get_paginate_by(self, queryset):
        paginate_by = Blog.objects.get_blog().entries_per_page
        return paginate_by

    def get_context_data(self, *args, **kwargs):
        context = super(AuthorView, self).get_context_data(*args, **kwargs)
        context['author'] = self.kwargs['author']
        return context

def entry_search(request):
    form = SearchForm()
    anry = None
    results = None
    total_results = None
    if 'queryset' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            anry = form.cleaned_data
            results = SearchQuerySet().models(Entry).filter(content=anry['queryset']).load_all()

            # Count total results
            total_results = results.count()

    return render(request, 'blog/search.html', {
        'form': form,
        'cd': anry,
        'results': results,
        'total_results': total_results}
    )
