from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.images import get_image_model_string
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.blocks import RichTextBlock, CharBlock, StructBlock

# Custom blocks for StreamField
class HeadingBlock(StructBlock):
    heading_text = CharBlock(required=True)
    size = blocks.ChoiceBlock(choices=[
        ('h1', 'H1'),
        ('h2', 'H2'),
        ('h3', 'H3'),
        ('h4', 'H4'),
    ], default='h2')

    class Meta:
        template = 'blocks/heading.html'
        icon = 'title'
        label = 'Heading'

# Custom snippet model
@register_snippet
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('slug'),
    ]
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'

# Custom page model
class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField([
        ('heading', HeadingBlock()),
        ('paragraph', RichTextBlock()),
    ], blank=True, use_json_field=True)
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    featured_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('category'),
            FieldPanel('featured_image'),
        ], heading="Blog information"),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('blog_authors', label="Author(s)"),
    ]

    class Meta:
        verbose_name = 'Blog Page'

# Orderable model for many-to-many relationship
class BlogPageAuthor(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='blog_authors')
    author = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
    )
    
    panels = [
        FieldPanel('author'),
    ]

# Custom snippet for products
@register_snippet
class Product(ClusterableModel):
    name = models.CharField(max_length=200)
    description = RichTextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock_quantity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    featured_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('category'),
            FieldPanel('price'),
            FieldPanel('stock_quantity'),
            FieldPanel('is_active'),
        ], heading="Product Information"),
        FieldPanel('description'),
        FieldPanel('featured_image'),
        InlinePanel('product_images', label="Additional Images"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

# Additional images for products
class ProductImage(Orderable):
    product = ParentalKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ForeignKey(
        get_image_model_string(),
        on_delete=models.CASCADE,
        related_name='+'
    )
    caption = models.CharField(max_length=250, blank=True)
    
    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]