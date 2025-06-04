from django.db import models

from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.images.models import Image
from wagtail.images.blocks import ImageChooserBlock

# Import your custom StreamField blocks
from stream import blocks  # Make sure 'stream.blocks' exists and is in INSTALLED_APPS

class BlogListingPage(Page):
    
    template = 'blog/blog_listing_page.html'
    
    custom_title = models.CharField(blank=True, max_length=100)
    
    content_panels = Page.content_panels + [
        FieldPanel('custom_title'),
    ]

    def get_context(self, request, *args, **kwargs):  # Fixed: should be get_context not _get_context
        context = super().get_context(request, *args, **kwargs)
        context['posts'] = BlogDetailsPage.objects.live().public()
        return context


class BlogDetailsPage(Page):    
    blog_title = models.CharField(max_length=100, blank=True, null=True)
    blog_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    content = StreamField(
        [
            ('text_and_title', blocks.TextAndTitleBlocks()),
            ('rich_text', blocks.RichTextBlocks()), 
            ('simple_text', blocks.SimpleRichTextBlocks()), 
            ('card_blocks', blocks.CardBlocks()), 
            ('cta_blocks', blocks.CTABlock()), 
        ],
        use_json_field=True,
        default=list,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('blog_title'),
        FieldPanel('blog_image'),
        FieldPanel('content'),
    ]
