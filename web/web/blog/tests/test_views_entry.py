from datetime import datetime
from test_plus.test import TestCase
from django.test import RequestFactory
from ..views import (IndexView)
from ..models import Blog, Entry
from web.users.models import User


class BaseTestCase(TestCase):
    """Basic test case."""

    def setUp(self):
        """Set up environment."""
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username='jacob',
            email='jacob@gmail.com',
            password='top_secret')
        self.blog = Blog(
            title="test",
            tag_line="new blog",
            entries_per_page=10,
            recents=5,
            recent_comments=5,
            author=self.user)
        self.blog.save()

    def tearDown(self):
        """Clean created user object."""
        self.user.delete()
        self.factory = None


class TestEntryList(BaseTestCase):
    """docstring for TestEntryList."""

    def test_empty_entry_list(self):
        """Test empty entry list."""
        # Instantiate the view
        view = IndexView()
        # Generate a fake request
        request = self.factory.get(self.reverse('blog:entry_index'))
        # Attach the use to the request
        request.user = self.user
        # Attach request to the view
        view.request = request
        # Check empty entry list
        self.assertEqual(len(view.get_queryset()), 0)
        # Check status
        self.response_302(view.get(request))

        # Check page redirect to new entry page
        response = self.client.get(self.reverse('blog:entry_index'), follow=True)
        self.assertRedirects(response, '/admin/login/?next=/blog/entry/new/')
        # After login
        self.client.login(username='jacob', password='top_secret')
        response_2 = self.client.get(self.reverse('blog:entry_index'), follow=True)
        self.assertRedirects(response_2, '/blog/entry/new/')

    def test_entry_list(self):
        """Test entry list."""
        # Instantiate the view
        view = IndexView()

        # Generate a fake request
        request = self.factory.get(self.reverse('blog:entry_index'))

        # Attach the use to the request
        request.user = self.user

        # Attach request to the view
        view.request = request

        # Create entry
        self.entry = Entry.objects.create(
            id=1,
            blog=self.blog,
            title="test",
            text='foo',
            created_by=self.user,
            published_date=datetime.today(),
            is_published=True)
        self.entry_2 = Entry.objects.create(
            id=2,
            blog=self.blog,
            title="test2",
            text='foo2',
            created_by=self.user,
            published_date=datetime.today(),
            is_published=True)

        # Check empty entry list
        self.assertEqual(len(view.get_queryset()), 2)

    def test_entries_slug(self):
        """Test entries slug."""
        # Create entry
        self.entry = Entry.objects.create(
            id=1,
            blog=self.blog,
            title="test",
            text='foo',
            created_by=self.user,
            published_date=datetime.today(),
            is_published=True)
        self.entry_2 = Entry.objects.create(
            id=2,
            blog=self.blog,
            title="test2",
            text='foo2',
            created_by=self.user,
            published_date=datetime.today(),
            is_published=True)
        self.assertEqual(self.entry.slug, "test")
        self.assertEqual(self.entry_2.slug, "test2")
        e1 = Entry.objects.get(pk=self.entry.pk)
        e2 = Entry.objects.get(pk=self.entry_2.pk)
        self.assertEqual(e1.slug, "test")
        self.assertEqual(e2.slug, "test2")

    def test_entry_existence(self):
        """Test entry existence."""
        Entry.objects.create(
            blog=self.blog,
            title="test",
            text='foo',
            created_by=self.user,
            published_date=datetime.strptime('2016-04-25', '%Y-%m-%d'),
            is_published=True)
        response = self.get(self.reverse('entry_details', args=['2016', '04', 'test']))
        self.assertEqual(response.status_code, 200)
