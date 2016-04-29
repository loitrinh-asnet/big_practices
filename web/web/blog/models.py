"""Public."""
from datetime import datetime
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from .validators import validate_title


# ABSTRACT BASE CLASS
class TimestampeModel(models.Model):
    """A abstract model.

    This class will include a created and modified timestamp field on all models.
    """

    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    # modified_date = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        """Meta."""

        abstract = True


class TitleAbstractModel(models.Model):
    """A abstract model.

    Which any model that inherits it will throw a validation error
    If anyone attempts to save a model with a title that doesn't start 'Django'.
    """

    # Customize form field validators
    title = models.CharField(max_length=1000, validators=[validate_title])

    class Meta:
        """Inner class."""

        abstract = True


class BlogManager(models.Manager):
    """Manager of blog model."""

    def get_blog(self):
        """To return a QuerySet with the properties you reuqire."""
        blogs = self.all()
        if blogs:
            return blogs[0]
        return None


class Blog(models.Model):
    """Blog model.

    title: Title of the Blog.
    tag_line: Tagline of the blog.
    entries_per_page: Number of entries to display on each page.
    recents: Number of recent entries to display in the sidebar.
    recent_comments: Number of recent comments to displat in the sidebar.
    """
    author = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=1000)
    tag_line = models.CharField(max_length=100)
    entries_per_page = models.IntegerField(default=10)
    recents = models.IntegerField(default=5)
    recent_comments = models.IntegerField(default=5)
    default = models.Manager()
    objects = BlogManager()

    def get_absolute_url(self):
        """Get absolute url."""
        return reverse("blog:blog_details", kwargs={'pk': self.id})

    def __str__(self):
        """Docstring."""
        return self.title

    def save(self, *args, **kwargs):
        """There should not be more than one Blog object"""
        if Blog.objects.count() == 1 and not self.id:
            raise Exception("Only one blog object allowed.")
        # Call the "real" save() method.
        super(Blog, self).save(*args, **kwargs)

    class Meta:
        """Model metadata."""

        ordering = ['title']


class EntryManager(models.Manager):
    """Manager of Entry model."""

    def get_queryset(self):
        """To return a QuerySet with the properties you reuqire."""
        return super(EntryManager, self).get_queryset().filter(
            is_published=True,
            published_date__lte=datetime.now())


class Entry(TimestampeModel):
    """Entry model."""

    blog = models.ForeignKey(Blog, null=True)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    text = models.TextField()
    summary = models.TextField()
    published_date = models.DateTimeField(null=True)
    is_published = models.BooleanField(default=True)
    is_comments_allowed = models.BooleanField(default=True)
    meta_keywords = models.TextField(blank=True, null=True)
    meta_descriptions = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, unique=False, null=True)

    default = models.Manager()
    objects = EntryManager()

    def __str__(self):
        """Docstring."""
        return self.title

    def get_number_comments(self):
        """Get number comments of certain entry."""
        return Comment.objects.filter(entry=self, is_spam=False).count()

    def get_absolute_url(self):
        """Get absolute url."""
        return reverse(
            'blog:entry_details',
            args=[
                self.created_date.year,
                self.created_date.strftime('%m'),
                self.created_date.strftime('%d'),
                self.slug
            ]
        )

    def save(self, *args, **kwargs):
        """Save."""
        if not self.slug:
            self.slug = slugify(self.title)[:50]

        return super(Entry, self).save(*args, **kwargs)

    class Meta(TimestampeModel.Meta):
        """Meta."""

        ordering = ['-created_date']
        verbose_name_plural = 'Blog entries'


class CommentManager(models.Manager):
    """Manager of Comment model."""

    def get_query(self):
        """To return a QuerySet with the properties you reuqire."""
        return super(CommentManager, self).get_queryset().filter(is_public=True)


class BaseComment(TimestampeModel):
    """BaseComment model.

    text: The comment text.
    entry: The entry this comment is created for.
    created_date: The date this comment was written on.
    user_name: The user name who wrote this comment.
    user_url: This user profile who wrote this comment.
    """

    text = models.TextField()
    entry = models.ForeignKey(Entry)
    user_name = models.CharField(max_length=100)
    user_url = models.URLField()


class Comment(BaseComment):
    """Comment model.

    create_by: The user who wrote this comment.
    is_spam: Is comment mark as spam?
    is_public: Null of comments waiting to be approved, True if approved.
    user_ip: Ip address from which this comment was made.
    user_agent: User agent of the comment.
    """

    create_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        unique=False,
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    is_spam = models.BooleanField(default=False)
    is_public = models.NullBooleanField(null=True, blank=True)
    user_agent = models.CharField(max_length=200, default='')

    default = models.Manager()
    objects = CommentManager()
