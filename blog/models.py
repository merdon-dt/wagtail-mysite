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
        MultiFieldPanel([
            InlinePanel('author_tags', label='Authors', min_num=1, max_num=3),
        ])
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