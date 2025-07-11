from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting

@register_setting
class SocialMediaLinks(BaseSiteSetting):
    facebook = models.URLField(max_length=200, blank=True, help_text="Facebook page URL")
    twitter = models.URLField(max_length=200, blank=True, help_text="Twitter/X profile URL")
    instagram = models.URLField(max_length=200, blank=True, help_text="Instagram profile URL")
    linkedin = models.URLField(max_length=200, blank=True, help_text="LinkedIn profile URL")

    panels = [
        MultiFieldPanel([
            FieldPanel('facebook'),
            FieldPanel('twitter'),
            FieldPanel('instagram'),
            FieldPanel('linkedin'),
        ], heading='Social Media Links'),
    ]

    class Meta:
        verbose_name = 'Social Media Links'
        verbose_name_plural = 'Social Media Links'
        
        
