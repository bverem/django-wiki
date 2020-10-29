from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ImagesCustomCMSConfig(AppConfig):
    name = "wiki.plugins.imagescustomcms"
    verbose_name = _("Wiki images (custom CMS)")
    label = "wiki_imagescustomcms"
