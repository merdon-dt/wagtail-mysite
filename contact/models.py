from django.db import models
from wagtail.fields import RichTextField
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.admin.panels import FieldPanel, InlinePanel, FieldRowPanel, MultiFieldPanel
from modelcluster.fields import ParentalKey


# Create your models here.


class FormField(AbstractFormField):
    page = ParentalKey("ContactPage", related_name="form_fields", on_delete=models.CASCADE)
    

class ContactPage(AbstractEmailForm):
    template = "contact/contact_page.html"
    
    intro = models.CharField(
        max_length=255,
        help_text="Text to describe the contact form",
        blank=True
    )
    thank_you_text = RichTextField(
        max_length=255,
        help_text="Text to display to users after they submit the form",
        blank=True
    )
    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        InlinePanel("form_fields", label="Form fields"),
        FieldPanel("thank_you_text"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel("subject"),
        ], heading="Email Settings"),
    ] 