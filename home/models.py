from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, \
    InlinePanel, PageChooserPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.search import index

from wagtail.core.blocks import TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, RichTextBlock, RawHTMLBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock

from wagtail.snippets.models import register_snippet

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase

from django.utils import translation
from django.http import HttpResponseRedirect

from django.utils import translation
from django.http import HttpResponseRedirect

class LanguageRedirectionPage(Page):

    def serve(self, request):
        # This will only return a language that is in the LANGUAGES Django setting
        language = translation.get_language_from_request(request)
        if language != 'fi' or language != 'se':
            language = 'fi'
        return HttpResponseRedirect(self.url + language + '/')
		

class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.CASCADE
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.CASCADE
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    content_panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True


# Carousel items

class CarouselItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)

    content_panels = [
        ImageChooserPanel('image'),
        FieldPanel('embed_url'),
        FieldPanel('caption'),
    ]

    class Meta:
        abstract = True

register_snippet(CarouselItem)


class HomePageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('HomePage', related_name='carousel_items')

class TranslatablePageMixin(models.Model):
    # One link for each alternative language
    # These should only be used on the main language page (english)
    fi_link = models.ForeignKey(Page, null=True, on_delete=models.SET_NULL, blank=True, related_name='+')
    se_link = models.ForeignKey(Page, null=True, on_delete=models.SET_NULL, blank=True, related_name='+')

    panels = [
        PageChooserPanel('fi_link'),
        PageChooserPanel('se_link'),
    ]

    def get_language(self):
        """
        This returns the language code for this page.
        """
        # Look through ancestors of this page for its language homepage
        # The language homepage is located at depth 3
        language_homepage = self.get_ancestors(inclusive=True).get(depth=3)

        # The slug of language homepages should always be set to the language code
        return language_homepage.slug


    # Method to find the main language version of this page
    # This works by reversing the above links

    def fi_page(self):
        """
        This finds the english version of this page
        """
        language = self.get_language()

        if language == 'fi':
            return self
        elif language == 'se':
            return type(self).objects.filter(se_link=self).first().specific


    # We need a method to find a version of this page for each alternative language.
    # These all work the same way. They firstly find the main version of the page
    # (english), then from there they can just follow the link to the correct page.

    def se_page(self):
        """
        This finds the french version of this page
        """
        fi_page = self.fi_page()

        if fi_page and fi_page.se_link:
            return fi_page.se_link.specific

    class Meta:
        abstract = True

class HomePage(Page, TranslatablePageMixin):
    body = RichTextField(blank=True)
    intro = RichTextField(blank=True)
    sidebar = RichTextField(blank=True)
    # image = models.ForeignKey(
    #     'wagtailimages.Image',
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name='+'
    # )

    subpage_types = ['SubPage',]
    
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="text"),
        FieldPanel('body', classname="text"),
        # FieldPanel('sidebar', classname="text"),
        # ImageChooserPanel('image'),
        InlinePanel('carousel_items', label="Carousel Item"),
        MultiFieldPanel(TranslatablePageMixin.panels, 'Language links')

    ]

class SubPage(Page, TranslatablePageMixin):
    body = RichTextField(blank=True)
    intro = RichTextField(blank=True)
    sidebar = RichTextField(blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )


    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="text"),
        FieldPanel('body', classname="text"),
        FieldPanel('sidebar', classname="text"),
        ImageChooserPanel('image'),
        MultiFieldPanel(TranslatablePageMixin.panels, 'Language links')

    ]


