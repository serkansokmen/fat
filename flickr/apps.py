from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FlickrConfig(AppConfig):
    name = 'flickr'
    verbose_name = _('Flickr')
