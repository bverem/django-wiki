from django import forms
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from wiki.core.plugins.base import PluginSidebarFormMixin
#from wiki.plugins.imagescustomcms import models


class SidebarForm(PluginSidebarFormMixin):
    def __init__(self, article, request, *args, **kwargs):
        self.article = article
        self.request = request
        super().__init__(*args, **kwargs)
        self.fields["image"].required = True
