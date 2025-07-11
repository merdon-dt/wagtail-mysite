from linecache import cache
from django.db import models
from wagtail.models import Orderable
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
# from autoslug import AutoSlugField
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, PageChooserPanel, InlinePanel, MultiFieldPanel
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

class MenuItem(Orderable):

    link_title = models.CharField(
        blank=True,
        null=True,
        max_length=50
    )
    link_url = models.CharField(
        max_length=500,
        blank=True
    )
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    open_in_new_tab = models.BooleanField(default=False, blank=True)

    page = ParentalKey("Menu", related_name="menu_items")

    panels = [
        FieldPanel("link_title"),
        FieldPanel("link_url"),
        PageChooserPanel("link_page"),
        FieldPanel("open_in_new_tab"),
    ]

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_url:
            return self.link_url
        return '#'

    @property
    def title(self):
        if self.link_page and not self.link_title:
            return self.link_page.title
        elif self.link_title:
            return self.link_title
        return 'Missing Title'


@register_snippet
class Menu(ClusterableModel):
    """The main menu clusterable model."""

    title = models.CharField(max_length=100)
    slug = models.SlugField(
        max_length=100,)

    panels = [
        MultiFieldPanel([
            FieldPanel("title"),
            FieldPanel("slug"),
        ], heading="Menu"),
        InlinePanel("menu_items", label="Menu Item")
    ]

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        key = make_template_fragment_key(
            'nav_menu'
        )
        cache.delete(key)
        return super().save(*args, **kwargs)