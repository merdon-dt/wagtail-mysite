



from rest_framework.fields import Field

class ImageSerializerField(Field):
    def to_representation(self, value):
        return {
            "url": value.file.url,
            "title": value.title,
            "width": value.width,
            "height": value.height
            # "some": "value"
        }
        
        
# blog/serializers.py
from rest_framework import serializers
from wagtail.api.v2.serializers import PageSerializer
from wagtail.api.v2.utils import get_full_url
from blog.models import BlogListingPage, BlogDetailsPage


class BlogListingPageSerializer(PageSerializer):
    """Serializer for blog listing page - only what you need."""
    
    posts_data = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogListingPage
        fields = PageSerializer.Meta.fields + [
            'custom_title',
            'posts_data',
        ]
    
    def get_posts_data(self, obj):
        """Get posts data matching your current JSON structure."""
        request = self.context['request']
        posts = BlogDetailsPage.objects.live().public()
        
        # Apply tag filtering if present (same as your current logic)
        tag = request.GET.get('tag')
        if tag:
            posts = posts.filter(tags__slug=tag)
        
        # Return the same structure you're already using
        return [
            {
                "id": post.id,
                "title": post.blog_title,
                "url": get_full_url(request, post.url),
                "image_url": get_full_url(request, post.blog_image.file.url) if post.blog_image else "",
                "image_alt": post.blog_image.title if post.blog_image else "",
            }
            for post in posts
        ]       