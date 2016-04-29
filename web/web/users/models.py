# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth.models import AbstractUser
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from allauth.socialaccount.models import SocialAccount
from tastypie.models import create_api_key

import hashlib


@python_2_unicode_compatible
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Name of User"), blank=True, max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})


class Profile(models.Model):
    """Extending the User model."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)

    def profile_image_url(self):
        """Display the user's facebook."""
        fb_uid = SocialAccount.objects.filter(user_id=self.user.id, provider='facebook')
        if len(fb_uid):
            return "http://graph.facebook.com/{}/picture?width=40&height=40".format(fb_uid[0].uid)
        return "http://www.gravatar.com/avatar/{}?s=40".format(hashlib.md5(self.user.email).hexdigest())

    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)

User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])
signals.post_save.connect(create_api_key, sender=User)
