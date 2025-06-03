from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, PageChooserPanel
from stream import blocks

class HomePage(Page):
    banner_title = RichTextField(blank=True)
    banner_cta = models.CharField(blank=True, max_length=50)
    banner_image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='+',
    )
    # Use ForeignKey instead of PageChooserField
    banner_page_link = models.ForeignKey(
        'wagtailcore.Page',  # or just Page
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='+',
    )

    content = StreamField(
        [
            ('cta', blocks.CTABlock()), 
        ],
        use_json_field=True,
        default=list,  # default must be iterable
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('banner_title'),
        FieldPanel('banner_cta'),
        FieldPanel('banner_image'),
        PageChooserPanel('banner_page_link', help_text='A page to link to'),  # Use PageChooserPanel instead of FieldPanel
    ]