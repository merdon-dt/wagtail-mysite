from importlib.metadata import PackageNotFoundError
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
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from wagtail.api import APIField
from taggit.models import TaggedItemBase
from modelcluster.contrib.taggit import ClusterTaggableManager

import json
from rest_framework.response import Response



# Import your custom StreamField blocks

# from mysite import api
from blog.fields import ImageSerializerField
from blog.serializers import BlogDetailsPageSerializer, CategorySerializer, TagSerializer
from stream import blocks
from stream.serializers import StreamSerializer  # Make sure 'stream.blocks' exists and is in INSTALLED_APPS


class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey('blog.BlogDetailsPage', related_name='tagged_items')

class BlogListingPage(RoutablePageMixin, Page):
    
    template = 'blog/blog_listing_page.html'
    subpage_types = ['blog.BlogDetailsPage', 'blog.ArticleBlogPage', 'blog.VideoBlogPage']
    parent_page_types = ['blog.BlogListingPage']
    max_count = 1
    
    custom_title = models.CharField(blank=True, max_length=100)
    
    content_panels = Page.content_panels + [
        FieldPanel('custom_title'),
    ]
    
    

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        posts = BlogDetailsPage.objects.live().public()
        if request.GET.get('tag'):
            tag = request.GET.get('tag')
            posts = posts.filter(tags__slug=tag)

        context["posts"] = posts
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
    def get_blog_list(self):
        return self.get_children().live().specific()
    
    api_fields = [
        APIField('custom_title'),
        APIField('blog_list', serializer=BlogDetailsPageSerializer(source='get_blog_list', many=True)),
    ]
    
    @route(r'^latest/?$', name='latest_blog_post')
    def latest_blog_post(self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)
        context['posts_limit'] = BlogDetailsPage.objects.live().public()[:1]
        return render(request, 'blog/latest_blogs.html', context)
    
    # @route(r"^api/tags/(?P<slug>[-\w]+)/$", name='tag_blogs')
    # def tag_blogs(self, request, slug):
    #     post_tags = BlogDetailsPage.objects.live().public().filter(tags__slug=slug)
    #     serializer = BlogDetailsPageSerializer(post_tags, many=True)
    #     return Response({"tag": slug, "posts": serializer.data})

    
    # def get_context(self, request, *args, **kwargs):  # Fixed: should be get_context not _get_context
    #     context = super().get_context(request, *args, **kwargs)
    #     context['posts'] = BlogDetailsPage.objects.live().public()
    #     return context
    

"""class BlogDetailsPage(Page):    
    
    template = 'blog/blog_details_page.html'
    subpage_types = []
    
    blog_title = models.CharField(max_length=100, blank=True, null=True)
    blog_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    categories = ParentalManyToManyField('blog.BlogCategory', blank=True)
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)

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
        FieldPanel('tags'),
        MultiFieldPanel([
            InlinePanel('author_tags', label='Authors', min_num=1, max_num=3),
        ]),
        MultiFieldPanel([
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ],heading='Categories'),
        FieldPanel('content'),
    ]
    
    api_fields = [ APIField("content"),
                  APIField("author_tags"),
                  ]
    
    def save(self, *args, **kwargs):
        # Clear preview cache
        preview_key = make_template_fragment_key('blog_post_preview', [self.id])
        cache.delete(preview_key)

        # Clear blog details cache
        # details_key = make_template_fragment_key('blog_details')
        # cache.delete(details_key)

        return super().save(*args, **kwargs)"""
        
class BlogDetailsPage(Page):
    """Parental blog detail page."""

    subpage_types = []
    parent_page_types = ['blog.BlogListingPage']
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    blog_title = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        help_text='Overwrites the default title',
    )
    blog_image = models.ForeignKey(
        "wagtailimages.Image",
        blank=False,
        null=True,
        related_name="+",
        on_delete=models.SET_NULL,
    )

    categories = ParentalManyToManyField("blog.BlogCategory", blank=True)

    content = StreamField(
        [
            ('text_and_title', blocks.TextAndTitleBlocks()),
            ('rich_text', blocks.RichTextBlocks()), 
            ('simple_text', blocks.SimpleRichTextBlocks()), 
            ('card_blocks', blocks.CardBlocks()), 
            ('cta_blocks', blocks.CTABlock()), 
        ],
        null=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel('blog_title'),
        FieldPanel('blog_image'),
        FieldPanel('tags'),
        MultiFieldPanel([
            InlinePanel('author_tags', label='Authors', min_num=1, max_num=3),
        ]),
        MultiFieldPanel([
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ],heading='Categories'),
        FieldPanel('content'),
    ]
    
    api_fields = [
                    APIField("blog_title"),
                    APIField("author_tags",),
                    APIField("blog_image", serializer=ImageSerializerField()),
                    APIField("tags", serializer=TagSerializer(source="tags.all")),
                    APIField("categories", serializer=CategorySerializer(source="categories.all")),
                    APIField("content", serializer=StreamSerializer()),
                  ]

    def save(self, *args, **kwargs):
        """Create a template fragment key.

        Then delete the key."""
        key = make_template_fragment_key(
            "blog_post_preview",
            [self.id]
        )
        cache.delete(key)
        return super().save(*args, **kwargs)
        

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
    
    @property
    def author_name(self):
        return self.author.author_name
    @property
    def author_website(self):
        return self.author.author_website
    @property
    def author_image(self):
        return self.author.author_image
    
    api_fields = [
        APIField("author_name"),
        APIField("author_website"),
        APIField("author_image", serializer=ImageSerializerField()),
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
        FieldPanel('tags'),
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
    
        
    api_fields = [ 
                  APIField("blog_title"),
                  APIField("custom_title"),
                  APIField("author_tags"),
                    APIField("blog_image", serializer=ImageSerializerField()),
                    APIField("tags", serializer=TagSerializer(source="tags.all")),
                    APIField("categories", serializer=CategorySerializer(source="categories.all")),
                    APIField("content", serializer=StreamSerializer()),
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
        FieldPanel('tags'),
        FieldPanel('blog_image'),
        MultiFieldPanel([
            InlinePanel('author_tags', label='Authors', min_num=1, max_num=3),
        ]),
        MultiFieldPanel([
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ],heading='Categories'),
        FieldPanel('content'),
    ]
    api_fields = [ 
                APIField("blog_title"),
                APIField("youtube_video_id"),
                APIField("author_tags"),
                APIField("blog_image", serializer=ImageSerializerField()),
                APIField("tags", serializer=TagSerializer(source="tags.all")),
                APIField("categories", serializer=CategorySerializer(source="categories.all")),
                APIField("content", serializer=StreamSerializer()),
                  ]
    
    class Meta:
        verbose_name = 'Video BLog Page'
        verbose_name_plural = 'Videos Blog Page'
        
        
        
        
        """from django.db import models
from django.shortcuts import render
from django.utils.safestring import mark_safe

from wagtail.models import Page, Orderable
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.models import Image
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.snippets.models import register_snippet

from modelcluster.fields import ParentalKey
from modelcluster.fields import ParentalManyToManyField
from django import forms
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from wagtail.api import APIField

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
        context["posts"] = posts
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
        # Removed use_json_field=True as it's default in Wagtail 4.0+
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
        ], heading='Categories'),
        FieldPanel('content'),
    ]
    
    # Custom properties for API serialization
    @property
    def categories_data(self):
        return [
            {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
            }
            for category in self.categories.all()
        ]
    
    @property
    def authors_data(self):
        return [
            {
                'id': author_tag.author.id,
                'author_name': author_tag.author.author_name,
                'author_image': {
                    'id': author_tag.author.author_image.id,
                    'title': author_tag.author.author_image.title,
                    'url': author_tag.author.author_image.file.url
                } if author_tag.author.author_image else None,
                'author_website': author_tag.author.author_website,
            }
            for author_tag in self.author_tags.all()
        ]
    
    # API fields with custom serialization
    api_fields = [
        APIField('blog_title'),
        APIField('blog_image'),
        APIField('authors_data'),
        APIField('categories_data'),
        APIField('content')
    ]
    
    def save(self, *args, **kwargs):
        # Clear preview cache
        preview_key = make_template_fragment_key('blog_post_preview', [self.id])
        cache.delete(preview_key)
        return super().save(*args, **kwargs)

@register_snippet
class BlogAuthor(models.Model):
    author_name = models.CharField(max_length=100)
    author_image = models.ForeignKey(
        "wagtailimages.Image", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    author_website = models.URLField(blank=True)
    
    panels = [
        MultiFieldPanel([
            FieldPanel('author_name'),
            FieldPanel('author_image'),
        ], heading='Author data'),
        MultiFieldPanel([
            FieldPanel('author_website')
        ], heading='Author website'),
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
    
    # Custom serialization for author data
    @property
    def author_data(self):
        return {
            'id': self.author.id,
            'author_name': self.author.author_name,
            'author_image': {
                'id': self.author.author_image.id,
                'title': self.author.author_image.title,
                'url': self.author.author_image.file.url
            } if self.author.author_image else None,
            'author_website': self.author.author_website,
        }
    
    api_fields = [
        APIField('author_data'),
    ]

@register_snippet
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
        ], heading='Categories'),
        FieldPanel('content'),
    ]
    
    # API fields for article blog page
    api_fields = BlogDetailsPage.api_fields + [
        APIField('custom_title'),
        APIField('subtitle'),
    ]
    
    class Meta:
        verbose_name = 'Article Blog Page'
        verbose_name_plural = 'Articles Blog Page'
        
    def __str__(self):
        return self.custom_title or self.blog_title or self.title
            
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
        ], heading='Categories'),
        FieldPanel('content'),
    ]
    
    # API fields for video blog page
    api_fields = BlogDetailsPage.api_fields + [
        APIField('youtube_video_id'),
    ]
    
    class Meta:
        verbose_name = 'Video Blog Page'
        verbose_name_plural = 'Videos Blog Page'
        
        
        
        

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
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
# from wagtail.api.fields import APIFields
# from wagtail.api import APIField
from wagtail.api import APIField



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
    
    api_fields = [  APIField('blog_title'), 
                    APIField('blog_image'), 
                    APIField('author_tags'), 
                    APIField('categories'), 
                    APIField('content')
                    ]
    
    def save(self, *args, **kwargs):
        # Clear preview cache
        preview_key = make_template_fragment_key('blog_post_preview', [self.id])
        cache.delete(preview_key)

        # Clear blog details cache
        # details_key = make_template_fragment_key('blog_details')
        # cache.delete(details_key)

        return super().save(*args, **kwargs)

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
"""      
