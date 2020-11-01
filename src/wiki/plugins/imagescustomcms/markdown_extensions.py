import markdown, urllib, json
from django.template.loader import render_to_string
from django.contrib.auth.models import AnonymousUser
from django.conf import settings as django_settings
from django.http import HttpRequest, QueryDict
from wiki.plugins.imagescustomcms import models
from wiki.plugins.imagescustomcms import settings

import importlib
FILE_VIEWS = importlib.import_module(settings.IMAGECUSTOMCMS_VIEW)
FILE_METHOD = getattr(FILE_VIEWS, settings.IMAGECUSTOMCMS_VIEW_METHOD)

#FILE_MODEL = getattr(importlib.import_module(settings.IMAGECUSTOMCMS_MODEL_APP), settings.IMAGECUSTOMCMS_MODEL)

IMAGE_RE = (
    r"(?:(?im)"
    +
    # Match '[image:N'
    r"\[image\:(?P<id>[0-9]+)"
    +
    # Match optional 'align'
    r"(?:\s+align\:(?P<align>right|left))?"
    +
    # Match optional 'size'
    r"(?:\s+size\:(?P<size>default|small|medium|large|orig))?"
    +
    # Match ']' and rest of line.
    # Normally [^\n] could be replaced with a dot '.', since '.'
    # does not match newlines, but inline processors run with re.DOTALL.
    r"\s*\](?P<trailer>[^\n]*)$"
    +
    # Match zero or more caption lines, each indented by four spaces.
    r"(?P<caption>(?:\n    [^\n]*)*))"
)



class ImageCustomCMSExtension(markdown.Extension):

    """ Images plugin markdown extension for django-wiki. """

    def extendMarkdown(self, md):
        md.inlinePatterns.add("dw-images", ImageCustomCMSPattern(IMAGE_RE, md), ">link")
        md.postprocessors.add("dw-images-cleanup", ImageCustomCMSPostprocessor(md), ">raw_html")


class ImageCustomCMSPattern(markdown.inlinepatterns.Pattern):
    """
    django-wiki image preprocessor
    Parse text for [image:N align:ALIGN size:SIZE] references.
    For instance:
    [image:id align:left|right]
        This is the caption text maybe with [a link](...)
    So: Remember that the caption text is fully valid markdown!
    """

    def handleMatch(self, m):
        image_id = None
        alignment = None
        size = settings.THUMBNAIL_SIZES["default"]

        image_id = m.group("id").strip()
        alignment = m.group("align")
        if m.group("size"):
            size = settings.THUMBNAIL_SIZES[m.group("size")]

        # Originally was just going to reverse, but I can't figure out how to deal with django-wiki's reverse override. So I'll access the method directly.
        qdict = QueryDict(urllib.parse.urlencode({'asset_id': image_id, 'return_type': 'json'}))
        request = HttpRequest()
        request.method = 'GET'
        request.GET = qdict
        request.user = AnonymousUser()
        image_data = FILE_METHOD(request).content
        if image_data:
            image_data = json.loads(image_data)
            image_data['full_url'] = settings.IMAGECUSTOMCMS_DOMAIN + image_data['url'] # Maybe I can remove this by rendering with Django?
            image_data['sorl_url'] = '/'.join(image_data['url'].split('/')[2:]) # Apparently sorl will try to be helpful and include MEDIA_ROOT in the URL, which Django already does with file.url; this makes the URL contain an extra MEDIA_ROOT folder and a subsequent error.
            print(image_data)
            caption = m.group("caption")
            trailer = m.group("trailer")

            caption_placeholder = "{{{IMAGECAPTION}}}"
            width = size.split("x")[0] if size else None
            html = render_to_string(
                "wiki/plugins/imagescustomcms/render.html",
                context={
                    "image_data": image_data,
                    "caption": caption_placeholder,
                    "align": alignment,
                    "size": size,
                    "width": width,
                },
            )
            html_before, html_after = html.split(caption_placeholder)
            placeholder_before = self.markdown.htmlStash.store(html_before)
            placeholder_after = self.markdown.htmlStash.store(html_after)
            return placeholder_before + caption + placeholder_after + trailer
        else:
            return ''


class ImageCustomCMSPostprocessor(markdown.postprocessors.Postprocessor):
    def run(self, text):
        """
        This cleans up after Markdown's well-intended placing of image tags
        inside <p> elements. The problem is that Markdown should put
        <p> tags around images as they are inline elements. However, because
        we wrap them in <figure>, we don't actually want it and have to
        remove it again after.
        """
        text = text.replace("<p><figure", "<figure")
        text = text.replace("</figure>\n</p>", "</figure>")
        return text
