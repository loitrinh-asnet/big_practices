"""User Resource."""
from django.conf.urls import url
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource, ALL
from tastypie.authentication import BasicAuthentication
from tastypie.authorization import Authorization

from web.users.models import User
from core.api.exceptions import CustomBadRequest
from core.api.utils import minimum_password_length, validate_password


class UserProfileResource(ModelResource):
    """User Resource.

    list:
        example: http://192.168.99.101:8000/api/v1/user/?username__startswith=a
        example: http://192.168.99.101:8000/api/v1/user__date_joined=__gte=2016-01-01
    """

    # Additional fields
    full_name = fields.CharField(attribute='get_full_name', blank=True)
    raw_password = fields.CharField(attribute=None, readonly=True, null=True, blank=True)

    class Meta:
        """Meta."""

        # Query set
        queryset = User.objects.all()

        # Authentication
        authentication = BasicAuthentication()

        # Authorization
        authorization = Authorization()

        # Resource name
        resource_name = 'user_profile'

        # Allowed methods
        allowed_methods = ['get', 'patch', 'put']

        # Allowed return data
        always_return_data = True

        # Specifies the collection of objects return ed in the GET list will be named
        collection_name = 'profile'

        # excludes
        excludes = ('is_active', 'is_staff', 'is_super', 'date_joined', 'last_login')

        # Ability to filter
        filtering = {
            'username': ALL,
            'date_joined': ['range', 'gt', 'gte', 'lt', 'lte'],
        }

        # Extra Actions
        extra_actions = [
            {
                "name": "login",
                "http_method": "POST",
                "resource_type": "list",
                "description": "Login into system",
                "fields": {
                    "username": {
                        "type": "string",
                        "required": True,
                        "description": "Username"
                    },
                    "password": {
                        "type": "string",
                        "required": True,
                        "description": "Password",
                    }
                }
            },
            {
                "name": "logout",
                "resource_type": "list",
                "methods": "GET",
                "description": "Logout"
            }
        ]

    def get_object_list(self, request):
        """Pre-request alterations to the request."""
        return super(UserProfileResource, self).get_object_list(request).filter(date_joined__gte="2016-01-01")

    def get_list(self, request, **kwargs):
        """Get current user profile."""
        kwargs["pk"] = request.user.pk
        return super(UserProfileResource, self).get_detail(request, **kwargs)

    def prepend_urls(self):
        return [
            # Login
            url(
                r'^(?P<resource_name>{0})/login{1}$'.format(
                    self._meta.resource_name,
                    trailing_slash()
                ),
                self.wrap_view('login'),
                name='api_login',
            ),
            # Logout
            url(
                r'^(?P<resource_name>{0})/logout{1}'.format(
                    self._meta.resource_name,
                    trailing_slash()
                ),
                self.wrap_view('logout'),
                name='api_logout',
            )
        ]

    def login(self, request, **kwargs):
        """Login into system.

        :argument
        {
            "username": "admin",
            "password": "abcd@1234",
        }

        :return
        {
          "email": "admin@gmail.com",
          "full_name": "",
          "is_super": true,
          "username": "admin"
        }
        """
        self.method_check(request, ['post'])
        data = self.deserialize(
            request,
            request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json')
        )

        username = data.get('username', '')
        password = data.get('password', '')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return self.create_response(
                    request,
                    {
                        'username': user.username,
                        'full_name': user.get_full_name(),
                        'email': user.email,
                        'is_super': user.is_superuser,
                    }
                )
            else:
                return self.create_response(
                    request,
                    {'success': False}
                )

    def logout(self, request, **kwargs):
        """Logout.

        :return
        {
            "success": "True" or "False"
        }
        """
        self.method_check(request, ['get'])
        self.is_authenticated(request)
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(
                request,
                {'success': True}
            )
        else:
            return self.create_response(
                request,
                {'success': False}
            )

    def obj_update(self, bundle, request=None, **kwargs):
        """Update user profile."""
        bundle = super(UserProfileResource, self).obj_update(bundle, request, **kwargs)
        password = bundle.data.get('password')
        if password:
            bundle.obj.set_password(password)
        bundle.obj.save()
        return bundle


class UserResource(ModelResource):
    """User Resource.

    list:
        example: http://192.168.99.101:8000/api/v1/user/?username__startswith=a
        example: http://192.168.99.101:8000/api/v1/user__date_joined=__gte=2016-01-01
    """

    # Additional fields
    full_name = fields.CharField(attribute='get_full_name', blank=True)

    class Meta:
        """Meta."""

        detail_uri_name = 'username'

        # Query set
        queryset = User.objects.all()

        # Authentication
        authentication = BasicAuthentication()

        # Authorization
        authorization = Authorization()

        # Resource name
        resource_name = 'users'

        # Allowed methods
        allowed_methods = ['get']

        # Allowed return data
        allowed_return_data = True

        # excludes
        excludes = ('is_active', 'is_staff', 'is_super', 'date_joined', 'last_login')

        # Ability to filter
        filtering = {
            'username': ALL
        }


class CreateUserResource(ModelResource):
    """Creating new User."""

    # user = fields.ForeignKey(UserProfileResource, 'user', full=True)

    class Meta:
        """Meta."""

        # Allowed methods
        allowed_methods = ['post']

        # Allowed return data
        allowed_return_data = True

        # Authentication
        authentication = BasicAuthentication()

        # Authorization
        authorization = Authorization()

        # Resource name
        resource_name = 'create_user'

        # Query set
        queryset = User.objects.all()

        # Extra Actions
        extra_actions = [
            {
                "name": "facebook_login",
                "http_method": "POST",
                "resource_type": "list",
                "description": "Login into system with facebook",
                "fields": {
                    "access_token": {
                        "type": "string",
                        "required": True,
                        "description": "Access Token"
                    },
                }
            },
        ]

    def prepend_urls(self):
        """A hook for adding own URLs or matching before the default URLs.

        Should return a list of individual URlconf lines
        """
        return [
            url(
                r'^(?P<resource_name>{0})/facebook_login{1}'.format(self._meta.resource_name, trailing_slash()),
                self.wrap_view('facebook_login'),
                name='api_facebook_login',
            ),
        ]

    def facebook_login(self, request, **kwargs):
        """Facebook sign up using django allauth tastypie."""
        data = self.deserialize(
            request,
            request.body,
            format=request.META.get('CONTENT_TYPE', 'application/json'))

        if 'access_token' not in data:
            raise CustomBadRequest(
                code='missing_key',
                message='Must provide {missing_key} when login with facebook.'.format(missing_key='access_token'))

        # Assign the access_token
        access_token = data.get('access_token', '')

        # Import some modules necessary
        # from allauth.socialaccount import providers
        from allauth.socialaccount.models import (SocialLogin, SocialToken, SocialApp)
        from allauth.socialaccount.providers.facebook.views import fb_complete_login
        from allauth.socialaccount.helpers import complete_social_login, complete_social_signup
        from allauth.socialaccount import providers
        from allauth.socialaccount.providers.facebook.provider import FacebookProvider, GRAPH_API_URL

        try:
            app = SocialApp.objects.get(provider='facebook')

            token = SocialToken(app=app, token=access_token)

            provider = providers.registry.by_id(FacebookProvider.id)
            print(provider.get_fields())
            print(GRAPH_API_URL)

            login = fb_complete_login(request, app, token)
            login.token = token
            login.state = SocialLogin.state_from_request(request)

            ret = complete_social_signup(request, login)
            print(ret)
            # If we get here we've succeeded
            return self.create_response(
                request,
                {
                    'success': True,
                    'user_id': request.user.pk,
                    'username': request.user.username,
                })
        except Exception as ex:
            print(ex)
            raise CustomBadRequest(
                code="missing_key",
                message="Can't login.")

    def hydrate(self, bundle):
        """Hydrate used to check it required fields are available in bundle.data or not."""
        required_user_fileds = ('username', "email", "first_name", "last_name", "raw_password")

        for field in required_user_fileds:
            if field not in bundle.data:
                raise CustomBadRequest(
                    code="missing_key",
                    message="Must provide {missing_key} when creating a user.".format(missing_key=field))

        # Validate password
        raw_password = bundle.data['raw_password']

        if not validate_password(raw_password):
            if len(raw_password) < minimum_password_length:
                raise CustomBadRequest(
                    code="invalid_password",
                    message="Your password should contain at least {length}".format(length=minimum_password_length))

            raise CustomBadRequest(
                code='invalid_password',
                message='Your password should no spaces.')

        bundle.data["password"] = make_password(raw_password)
        return bundle

    def dehydrate(self, bundle):
        """
        dehydate.

        Used to delete raw_password field
        """
        bundle.data['key'] = bundle.obj.api_key.key
        try:
            del bundle.data["raw_password"]
        except KeyError:
            pass
        return bundle

    def obj_create(self, bundle, **kwargs):
        """
        obj_create.

        Used to check if there is any other user with same username and email.
        """
        try:
            email = bundle.data["email"]
            username = bundle.data["username"]

            # If if there is any exisiting  user with same username or email address
            if User.objects.get(email=email):
                raise CustomBadRequest(
                    code="duplicate_exception",
                    message="That email is already used.")

            if User.objects.filter(username=username):
                raise CustomBadRequest(
                    code="duplicate_exception",
                    message="That username is already used.")
        except KeyError as missing_key:
            raise CustomBadRequest(
                code="missing_key",
                message="Must provide {missing_key} when creating a user.".format(missing_key=missing_key))
        except User.DoesNotExist:
            pass
        return super(CreateUserResource, self).obj_create(bundle, **kwargs)


