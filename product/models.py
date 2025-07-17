from django.db import models
from wagtail.models import Page, Orderable
from wagtail.snippets.models import register_snippet
from wagtail.fields import RichTextField
from wagtail.api import APIField
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from blog.fields import ImageSerializerField
from product.serializers import ProductImageSerializer
from django import forms
from wagtail.admin.forms.pages import WagtailAdminPageForm

class HideTitleAdminForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'title' in self.fields:
            self.fields['title'].widget = forms.HiddenInput()

@register_snippet
class ProductCategory(models.Model):
    category_name = models.CharField(max_length=100)
    category_description = RichTextField(max_length=255)
    
    panels = [
        FieldPanel('category_name'),
        FieldPanel('category_description'),
    ]
    
    api_fields = [
        APIField('category_name'),
        APIField('category_description'),
    ]
    def __str__(self):   
        return self.category_name
    
class ProductImage(Orderable):
    product = ParentalKey('product.ProductDetailsPage', on_delete=models.CASCADE, related_name='product_images')
    product_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    api_fields = [
        APIField('product_image', serializer=ProductImageSerializer)
    ]
    
class ProductListingPage(Page):
    max_count = 1
    subpage_types = ['product.ProductDetailsPage']
    
class ProductDetailsPage(Page):
    subpage_types = []
    parent_page_types = ['product.ProductListingPage']
    base_form_class = HideTitleAdminForm

    
    custom_title = models.CharField(max_length=100, verbose_name="Product Title")
    product_description = RichTextField(max_length=255, blank=False, null=False, default=None)
    product_code = models.CharField(max_length=100, blank=False, null=False)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('custom_title'),
        FieldPanel('product_description'),
        FieldPanel('product_code'),
        FieldPanel('category'),
        FieldPanel('product_price'),
        FieldPanel('stock_quantity'),
        FieldPanel('is_active'),
    ]
    
    api_fields = [
        APIField('custom_title'),
        APIField('product_description'),
        APIField('product_code'),
        APIField('category'),
        APIField('product_price'),
        APIField('stock_quantity'),
        APIField('is_active'),
    ]
    
    def save(self, *args, **kwargs):
        if self.custom_title:
            self.title = self.custom_title
        super().save(*args, **kwargs)
    def get_admin_display_title(self):
        return self.custom_title or super().get_admin_display_title()


    def __str__(self):
        return self.custom_title