from django.apps import AppConfig
from django.core.checks import register
from django.utils.translation import gettext_lazy as _

from . import checks


class ImagesCustomCMSConfig(AppConfig):
    name = "wiki.plugins.imagescustomcms" # This line is preventing the images from being inserted. Sidebar.html isn't being loaded.
    verbose_name = _("Wiki images (custom CMS)")
    label = "wiki_imagescustomcms"

    def ready(self):
        register(
            checks.check_for_required_installed_apps,
            checks.Tags.required_installed_apps,
        )
