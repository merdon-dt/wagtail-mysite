from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel

# Create your models here.

class Flex(Page):
    # content = StreamField(
        
    # )
    subtitle = models.CharField(max_length=100)
    
    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
    ]