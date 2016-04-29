"""Public."""
from .models import Blog


def is_blog_installed():
    """Docstring."""
    return Blog.objects.get_blog()
