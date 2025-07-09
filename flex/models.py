from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.blocks import RichTextBlock  # Import RichTextBlock here
from stream import blocks  # Your custom blocks like TextAndTitleBlocks

class Flex(Page):
    template = 'flex/flex_page.html'
    content = StreamField(
        [
            ('text_and_title', blocks.TextAndTitleBlocks()),
            ('rich_text', blocks.RichTextBlocks()), 
            ('simple_text', blocks.SimpleRichTextBlocks()), 
            ('card_blocks', blocks.CardBlocks()), 
            ('cta_blocks', blocks.CTABlock()), 
            ('button_blocks', blocks.SingleButtonBlock()), 
        ],
        use_json_field=True,
        default=list,  # default must be iterable
        blank=True,
    )

    subtitle = models.CharField(max_length=100)

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('content'),
    ]
