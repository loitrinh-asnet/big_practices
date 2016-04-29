"""Public."""
from web.users.models import User
from web.blog.models import Blog
from tastypie.validation import CleanedDataFormValidation


class EntryValidation(CleanedDataFormValidation):
    """Validation that makes use for a given Form."""

    def is_valid(self, bundle, request=None):
        """Validate the bunde with the given form."""
        data = bundle.data

        if data is None:
            data = {}

        if request:
            if not data.get('created_by', None):
                user = User.objects.get(username=request.user.username)
                data['created_by'] = user
            if not data.get('blog', None):
                blog = Blog.objects.get(author=user)
                data['blog'] = blog

        form = self.form_class(data, instance=bundle.obj)

        if form.is_valid():
            bundle.data = form.cleaned_data
            return {}

        return form.errors
