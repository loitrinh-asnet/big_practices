from django.test import TestCase
from django.core.urlresolvers import reverse
from web.users.models import User
from ..models import Blog


# Create your tests here.
class BlogTestCase(TestCase):

    def setUp(self):
        """The test runner will run this method prior to each test."""
        self.user = User.objects.create_superuser('john', 'lennon@thebeatles.com', 'johnpassword')

    def test_blog_install_redirect(self):
        """Check that the blog redirects to install page when there is no blog installed."""
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 302)

    def test_blog_install_status(self):
        """Check that the blog install redirects to login page when user is logged in."""
        response = self.client.get('/blog/install/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.redirect_chain), 1)

    def test_entry_new_redirect(self):
        self.client.login(username='john', password='johnpassword')
        Blog.objects.create(
            title='test',
            tag_line='test',
            entries_per_page=10,
            recents=5,
            recent_comments=5,
            author=self.user)

        response = self.client.get(reverse('blog:entry_index'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_redirect_to_login_page_from_new_entry_page(self):
        """Check that the blog redirects to login page when there is no entry created."""
        response = self.client.get(reverse('blog:entry_new'))
        self.assertRedirects(response, '/admin/login/?next=/blog/entry/new/')

    def test_single_existence(self):
        """Test that the blog is created only once """
        self.client.login(username='john', password='johnpassword')
        self.blog = Blog(
            title="test",
            tag_line="new blog",
            entries_per_page=10,
            recents=5,
            recent_comments=5,
            author=self.user)
        self.blog.save()
        blog = Blog(
            title="test",
            tag_line="new blog",
            entries_per_page=10,
            recents=5,
            recent_comments=5,
            author=self.user)

        # should raise Exception when another blog is created
        self.assertRaises(Exception, blog.save)
        blog = Blog.objects.get()
        blog.title = 'edited'
        blog.save()
        self.assertEqual(Blog.objects.count(), 1)
        self.assertEqual(Blog.objects.get().title, 'edited')
