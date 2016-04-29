"""MIXINS."""
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from datetime import datetime
from django.contrib import messages
from .models import Blog, Entry
from web.users.models import User


def handle404(view_function):
    """"."""
    def wrapper(*args, **kwargs):
        try:
            return view_function(*args, **kwargs)
        except ObjectDoesNotExist:
            raise Http404


class Handle404Mixin(object):
    """A handle404 mixin."""

    @method_decorator(handle404)
    def dispatch(self, request, *args, **kwargs):
        """Docstring."""
        return super(Handle404Mixin, self).dispatch(request, *args, **kwargs)


class LoginRequireMixin(object):
    """
    Authentication.

    A Mixin which restricts a view to only loggedin users might look something.
    """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """Docstring."""
        return super(LoginRequireMixin, self).dispatch(request, *args, **kwargs)


class AdminRequireMixin(object):
    """Authentication."""

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        """Docstring."""
        return super(AdminRequireMixin, self).dispatch(request, *args, **kwargs)


class PermissionsRequiredMixin(object):
    """
    Authorization.

    View mixin which verifies that the logged in user has the specified permissions.

    Settings:
        'required_permissions' - list/tupple of required permissions
    """

    required_permissions = ()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """dispatch."""
        if not request.user.has_perms(self.required_permissions):
            messages.error(
                request,
                'You do not have the permission required to perform the requested operation.',
                'requested operation.')
            return HttpResponseRedirect(reverse('blog:entry_index'))
        return super(PermissionsRequiredMixin, self).dispatch(request, *args, **kwargs)


class BlogActionMixin(object):
    """Validation."""

    model = Blog

    @property
    def success_msg(self):
        """Succee message."""
        return "hi"

    def form_valid(self, form):
        """Form valid."""
        messages.info(self.request, self.success_msg)
        form.instance.author = self.request.user
        return super(BlogActionMixin, self).form_valid(form)


class EntryActionMixin(object):
    """Validation."""

    model = Entry

    @property
    def success_msg(self):
        """Succee message."""
        return "hi"

    def form_valid(self, form):
        """Form valid."""
        form.instance.author = self.request.user
        form.instance.is_published = True
        form.instance.published_date = datetime.now()
        messages.info(self.request, self.success_msg)
        return super(EntryActionMixin, self).form_valid(form)

    def get_success_url(self):
        """Get success url."""
        blog_entry = self.object
        if blog_entry.is_published:
            return blog_entry.get_absolute_url()
        else:
            return reverse('entry_edit', args=[blog_entry.id]) + '?done'
