# serializers.py
from rest_framework import serializers
from wagtail.api.v2.serializers import PageSerializer
from wagtail.images.api.fields import ImageRenditionField
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = 'product.Category'  # Use your actual app name
        fields = ['id', 'name', 'description', 'slug']

class ProductImageSerializer(serializers.ModelSerializer):
    image = ImageRenditionField('fill-400x300')
    
    class Meta:
        model = 'product.ProductImage'  # Use your actual app name
        fields = ['image', 'caption']

# ✅ FIXED: Use ModelSerializer for non-Page models
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    featured_image = ImageRenditionField('fill-600x400', read_only=True)
    images = ProductImageSerializer(source='product_images', many=True, read_only=True)
    
    class Meta:
        model = 'product.Product'  # Use your actual app name
        fields = [
            'id', 'name', 'description', 'price', 'category',
            'stock_quantity', 'is_active', 'featured_image',
            'images', 'created_at', 'updated_at'
        ]

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class BlogPageAuthorSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    
    class Meta:
        model = 'product.BlogPageAuthor'  # Use your actual app name
        fields = ['author']

# ✅ FIXED: Use PageSerializer for Page models
class CustomBlogPageSerializer(PageSerializer):
    category = CategorySerializer(read_only=True)
    featured_image = ImageRenditionField('fill-800x600', read_only=True)
    authors = BlogPageAuthorSerializer(source='blog_authors', many=True, read_only=True)
    
    class Meta:
        model = 'product.BlogPage'  # Use your actual app name
        fields = PageSerializer.Meta.fields + [
            'date', 'intro', 'body', 'category', 'featured_image', 'authors'
        ]

# ✅ ALTERNATIVE: If you want to include body content in different serializers
class BlogPageListSerializer(PageSerializer):
    """Lighter serializer for list views"""
    category = CategorySerializer(read_only=True)
    featured_image = ImageRenditionField('fill-400x300', read_only=True)
    
    class Meta:
        model = 'product.BlogPage'
        fields = PageSerializer.Meta.fields + [
            'date', 'intro', 'category', 'featured_image'
        ]

class BlogPageDetailSerializer(PageSerializer):
    """Full serializer for detail views"""
    category = CategorySerializer(read_only=True)
    featured_image = ImageRenditionField('fill-800x600', read_only=True)
    authors = BlogPageAuthorSerializer(source='blog_authors', many=True, read_only=True)
    
    class Meta:
        model = 'product.BlogPage'
        fields = PageSerializer.Meta.fields + [
            'date', 'intro', 'body', 'category', 'featured_image', 'authors'
        ]

# ✅ CUSTOM STREAMFIELD SERIALIZER (if needed)
class StreamFieldSerializer(serializers.Field):
    """Custom serializer for StreamField content"""
    def to_representation(self, value):
        result = []
        for block in value:
            block_data = {
                'type': block.block_type,
                'value': block.value,
                'id': str(block.id)
            }
            
            # Handle image blocks specially
            if block.block_type == 'image':
                if block.value:
                    from wagtail.images import get_image_model
                    Image = get_image_model()
                    try:
                        image = Image.objects.get(pk=block.value)
                        block_data['value'] = {
                            'image_url': image.get_rendition('fill-800x600').url,
                            'thumbnail_url': image.get_rendition('fill-200x200').url,
                            'alt_text': image.default_alt_text,
                            'title': image.title,
                        }
                    except Image.DoesNotExist:
                        block_data['value'] = None
                        
            result.append(block_data)
        return result

# ✅ BLOG PAGE SERIALIZER WITH CUSTOM STREAMFIELD
class BlogPageWithStreamFieldSerializer(PageSerializer):
    category = CategorySerializer(read_only=True)
    featured_image = ImageRenditionField('fill-800x600', read_only=True)
    authors = BlogPageAuthorSerializer(source='blog_authors', many=True, read_only=True)
    body = StreamFieldSerializer(read_only=True)
    
    class Meta:
        model = 'product.BlogPage'
        fields = PageSerializer.Meta.fields + [
            'date', 'intro', 'body', 'category', 'featured_image', 'authors'
        ]