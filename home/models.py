from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, PageChooserPanel, InlinePanel, MultiFieldPanel
from modelcluster.fields import ParentalKey
import blog
from stream import blocks
from wagtail.api import APIField

class HomePage(Page):
    
    subpage_types = ['blog.BlogListingPage', 'contact.ContactPage', 'flex.Flex']
    parent_page_types = ['wagtailcore.Page']
    max_count = 1
    
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
        MultiFieldPanel([
            FieldPanel('banner_title'),
            FieldPanel('banner_cta'),
            FieldPanel('banner_image'),
            PageChooserPanel('banner_page_link', help_text='A page to link to'),
        ], heading='Banner'),
    
            FieldPanel('content'),
         MultiFieldPanel([
            InlinePanel('carousel_items', label='Carousel Images', max_num=5, min_num=1),
        ], heading='Carousel'),
    ]
    
    api_fields = [
                    APIField("banner_title"),
                    APIField("banner_cta"),
                    APIField("banner_image"),
                    APIField("banner_page_link"),   
                    APIField("carousel_items"),
                    ]

    class Meta:
        verbose_name = 'Home Page'
        verbose_name_plural = 'Home Pages'
    
    
class CarouselImageBlock(Orderable):
    page = ParentalKey('home.HomePage', related_name='carousel_items')
    image = models.ForeignKey(
        'wagtailimages.Image', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    title = models.CharField(max_length=100, blank=True)
    caption = RichTextField(
        blank=True, 
        features=['bold','italic', 'ol', 'ul']  # Fixed: 'features' not 'feature'
    )
    
    panels = [  # Fixed: 'panels' not 'content_panels' for Orderable models
        FieldPanel('image'),
        FieldPanel('title'),
        FieldPanel('caption'),
    ]
    
    api_fields = [
        APIField("image"),
        APIField("title"),
        APIField("caption"),
    ]
    
    class Meta:
        verbose_name = 'Carousel Image'
        verbose_name_plural = 'Carousel Images'
            
