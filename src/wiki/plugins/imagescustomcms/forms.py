from django import forms
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from wiki.core.plugins.base import PluginSidebarFormMixin
from wiki.plugins.images import models
from wiki.plugins.imagescustomcms import settings

'''class ImagesCustomCMSForm(PluginSidebarFormMixin, settings.IMAGECUSTOMCMS_FORM):
    def __init__(self, article, request, *args, **kwargs):
        self.article = article
        self.request = request
        super().__init__(*args, **kwargs)'''
