from django.db import models
from django.shortcuts import render
from django.utils.safestring import mark_safe

from wagtail.models import Page, Orderable
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.images.models import Image
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet

from modelcluster.fields import ParentalKey
from modelcluster.fields import ParentalManyToManyField
from django import forms



import json




# Import your custom StreamField blocks
from stream import blocks  # Make sure 'stream.blocks' exists and is in INSTALLED_APPS

class BlogListingPage(RoutablePageMixin, Page):
    
    template = 'blog/blog_listing_page.html'
    
    custom_title = models.CharField(blank=True, max_length=100)
    
    content_panels = Page.content_panels + [
        FieldPanel('custom_title'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        posts = BlogDetailsPage.objects.live().public()
        context["posts"] = posts  # ✅ Add this line back
        context["categories"] = BlogCategory.objects.all()


        # Optional: JSON version for React
        serialized_posts = [
            {
                "id": post.id,
                "title": post.blog_title,
                "url": post.url,
                "image_url": post.blog_image.file.url if post.blog_image else "",
                "image_alt": post.blog_image.title if post.blog_image else "",
            }
            for post in posts
        ]
        context["posts_json"] = mark_safe(json.dumps(serialized_posts))
        return context
    
    @route(r'^latest/?$', name='latest_blog_post')
    def latest_blog_post(self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)
        context['posts_limit'] = BlogDetailsPage.objects.live().public()[:1]
        return render(request, 'blog/latest_blogs.html', context)

    
    # def get_context(self, request, *args, **kwargs):  # Fixed: should be get_context not _get_context
    #     context = super().get_context(request, *args, **kwargs)
    #     context['posts'] = BlogDetailsPage.objects.live().public()
    #     return context
    

class BlogDetailsPage(Page):    
    template = 'blog/blog_details_page.html'
    blog_title = models.CharField(max_length=100, blank=True, null=True)
    blog_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)

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
        MultiFieldPanel([
            InlinePanel('author_tags', label='Authors', min_num=1, max_num=3),
        ]),
        MultiFieldPanel([
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ],heading='Categories'),
        FieldPanel('content'),
    ]

@register_snippet
class BlogAuthor(models.Model):
    author_name = models.CharField(max_length=100)
    author_image = models.ForeignKey("wagtailimages.Image", on_delete=models.SET_NULL, null=True, blank=True)
    author_website = models.URLField(blank=True)
    
    panels = [
        MultiFieldPanel([
            FieldPanel('author_name'),
            FieldPanel('author_image'),], heading='Author data'),
        MultiFieldPanel([
            FieldPanel('author_website')], heading='Author website'),
    ]
    
    def __str__(self):
        return self.author_name
    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'
        
        
        
class AuthorTag(Orderable):
    page = ParentalKey(BlogDetailsPage, related_name='author_tags')
    author = models.ForeignKey(BlogAuthor, on_delete=models.CASCADE)
    
    panels = [
        FieldPanel('author')
    ]
    

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(
        verbose_name="slug",
        allow_unicode=True,
        max_length=255,
        help_text='A slug to identify posts by this category',
    )  
    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]  
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
register_snippet(BlogCategory)

class ArticleBlogPage(BlogDetailsPage):
    template = 'blog/article_blog_page.html'
    
    custom_title = models.CharField(max_length=100, blank=True, null=True)
    subtitle = models.CharField(max_length=100, blank=True, null=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('blog_title'),
        FieldPanel('custom_title'),
        FieldPanel('subtitle'),
        FieldPanel('blog_image'),
        MultiFieldPanel([
            InlinePanel('author_tags', label='Authors', min_num=1, max_num=3),
        ]),
        MultiFieldPanel([
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ],heading='Categories'),
        FieldPanel('content'),
    ]
    class Meta:
        verbose_name = 'Article BLog Page'
        verbose_name_plural = 'Articles Blog Page'
        
    def __str__(self):
        return self.custom_title
            
            
class VideoBlogPage(BlogDetailsPage):
    template = 'blog/video_blog_page.html'
    
    youtube_video_id = models.CharField(max_length=100, blank=True, null=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('blog_title'),
        FieldPanel('youtube_video_id'),
        FieldPanel('blog_image'),
        MultiFieldPanel([
            InlinePanel('author_tags', label='Authors', min_num=1, max_num=3),
        ]),
        MultiFieldPanel([
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ],heading='Categories'),
        FieldPanel('content'),
    ]
    
    class Meta:
        verbose_name = 'Video BLog Page'
        verbose_name_plural = 'Videos Blog Page'