import datetime
from django.test import TestCase
from tastypie.test import ResourceTestCaseMixin
from web.users.models import User
from web.blog.models import Entry

class EntryResourceTest(ResourceTestCaseMixin, TestCase):

    def setUp(self):
        super(EntryResourceTest, self).setUp()

        #Create a user
        self.api_name = 'api/v1/entry/'
        self.username = 'loitrinh'
        self.password = 'abc@123'
        self.email = 'loitrinh@gmail.com'
        self.user = User.objects.create_user(self.username, self.email, self.password)

        # Fetch the Entry object we will use in testing
        self.entry_1 = Entry.objects.get(slug='first-post')

        # We also build a detail URI, since we will be using it all over
        self.detail_url = 'api/v1/entry/{0'.format(self.entry_1.pk)

        # The data we will send on POST requests. AGain , because we will use it frequently
        self.post_data = {
            'user': '/api/v1/user/{0}'.format(self.entry_1.pk),
            'title': 'Second Post!',
            'text': "The dehydrate method takes a now fully-populated bundle.data",
            'slug': 'second-post',
            'created_date': '2016-04-08T22:05:12'
        }

    def get_credentials(self):
        return self.create_basic(username=self.username, password=self.password)

    def test_get_list_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.get(self.api_name, format='json'))

    def test_get_list_json(self):
        resp = self.api_client.get(self.api_name, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        # Scope out the data for correctness
        self.assertEqual(len(self.deserialize(resp)['objects']), 12)

        # Checking an entry structure for the expected data
        self.assertEqual(self.deserialize(resp)['objects'][0], {
            'pk': str(self.entry_1.pk),
            'user': '/api/v1/user/{0}/'.format(self.user.pk),
            'title': 'First post',
            'slug': 'first-post',
            'created': '2012-05-01T19:13:42',
            'resource_uri': '/api/v1/entry/{0}/'.format(self.entry_1.pk)
        })

    def test_get_list_xml(self):
        self.assertValidXMLResponse(self.api_client.get(self.api_name, format='xml', authentication=self.get_credentials()))


    def test_get_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client(self.detail_url, format='json'))

    def test_get_detail_json(self):
        resp = self.api_client.get(self.detail_url, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        # Just verify the keys, not all the data
        self.assertKeys(self.deserialize(resp), ['created', 'slug', 'title', 'user'])
        self.assertEqual(self.deserialize(resp)['name'], 'First post')

    def test_post_list_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.post(self.api_name, format='json', data=self.post_data))

    def test_post_list(self):
        self.assertEqual(Entry.objects.count(), 5)
        self.assertHttpCreated(self.api_client.post(self.api_name, format='json', data= self.post_data, authentication=self.get_credentials()))
        self.assertEqual(Entry.objects.count(), 6)

    def test_put_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.put(self.detail_url, format='json', data={}))

    def test_put_detail(self):
        # Gradb the current data and modify it slightly
        original_data=self.deserialize(self.api_client.get(self.api_name, format='json', authentication=self.get_credentials()))
        new_data=original_data.copy()
        new_data['title']='Updated: First post'

        # Make sure the count hasn't changed
        self.assertEqual(Entry.objects.count(), 5)
        self.assertHttpAccepted(self.api_client.put(self.detail_url, format='json', data=new_data, authentication=self.get_credentials()))
        self.assertEqual(Entry.objects.count(), 5)

        # Check for updated data
        entry=Entry.objects.get(pk=25)
        self.assertEqual(entry.title, 'Updated: First post')
        self.assertEqual(entry.slug, 'first-post')

    def test_delete_detail_unauthenticated(self):
        self.assertHttpUnauthorized(self.api_client.delete(self.detail_url, format='json'))

    def test_delet_detail(self):
        self.assertEqual(EntryResourceTest.objects.count(), 5)
        self.assertHttpAccepted(self.api_client.delete(self.detail_url, format='json', authentication=self.get_credentials()))
        self.assertEqual(EntryResourceTest.objects.count(), 4)
