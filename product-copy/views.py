# api.py (or views.py)
from wagtail.api.v2.views import PagesAPIViewSet, BaseAPIViewSet
from wagtail.api.v2.filters import FieldsFilter, OrderingFilter, SearchFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

class CustomPagesAPIViewSet(PagesAPIViewSet):
    filter_backends = [FieldsFilter, OrderingFilter, SearchFilter]
    meta_fields = ['type', 'detail_url', 'html_url', 'slug', 'first_published_at']
    body_fields = ['title', 'meta', 'parent']
    listing_default_fields = ['title', 'meta', 'parent']
    nested_default_fields = ['title', 'meta']
    detail_only_fields = ['body']
    name = 'pages'

class BlogPageAPIViewSet(BaseAPIViewSet):
    filter_backends = [FieldsFilter, OrderingFilter, SearchFilter]
    meta_fields = ['type', 'detail_url', 'html_url', 'slug', 'first_published_at']
    body_fields = ['title', 'date', 'intro', 'body', 'category', 'featured_image', 'authors']
    listing_default_fields = ['title', 'date', 'intro', 'category', 'featured_image']
    nested_default_fields = ['title', 'date', 'intro']
    detail_only_fields = ['body']
    name = 'blog_pages'

    def get_model(self):
        from .models import BlogPage
        return BlogPage

    def get_queryset(self):
        return self.get_model().objects.live().public().select_related('category').prefetch_related('blog_authors__author')

    def get_serializer_class(self):
        # Use different serializers for list vs detail
        if self.action == 'list':
            from .serializers import BlogPageListSerializer
            return BlogPageListSerializer
        else:
            from .serializers import CustomBlogPageSerializer
            return CustomBlogPageSerializer

# ✅ FIXED: Use BaseAPIViewSet for non-Page models
class ProductAPIViewSet(BaseAPIViewSet):
    filter_backends = [FieldsFilter, OrderingFilter, SearchFilter]
    body_fields = ['name', 'description', 'price', 'category', 'stock_quantity', 'is_active', 'featured_image', 'images']
    meta_fields = ['created_at', 'updated_at']
    listing_default_fields = ['name', 'price', 'category', 'stock_quantity', 'is_active', 'featured_image']
    nested_default_fields = ['name', 'price', 'category']
    detail_only_fields = ['description', 'images']
    name = 'products'

    def get_model(self):
        from .models import Product
        return Product

    def get_queryset(self):
        queryset = self.get_model().objects.select_related('category').prefetch_related('product_images')
        
        # Custom filtering
        category = self.request.query_params.get('category')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        in_stock = self.request.query_params.get('in_stock')
        
        if category:
            queryset = queryset.filter(category__slug=category)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)
            
        return queryset

    def get_serializer_class(self):
        from .serializers import ProductSerializer
        return ProductSerializer

    @action(detail=False, methods=['get'])
    def categories(self, request):
        from .models import Category
        from .serializers import CategorySerializer
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        threshold = int(request.query_params.get('threshold', 10))
        products = self.get_queryset().filter(stock_quantity__lte=threshold)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class CategoryAPIViewSet(BaseAPIViewSet):
    filter_backends = [FieldsFilter, OrderingFilter, SearchFilter]
    body_fields = ['name', 'description', 'slug']
    meta_fields = []
    listing_default_fields = ['name', 'description', 'slug']
    nested_default_fields = ['name', 'slug']
    name = 'categories'

    def get_model(self):
        from .models import Category
        return Category

    def get_queryset(self):
        return self.get_model().objects.all()

    def get_serializer_class(self):
        from .serializers import CategorySerializer
        return CategorySerializer

    @action(detail=False, methods=['get'])
    def products(self, request):
        """Get all products for a specific category"""
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response({'error': 'category_id parameter is required'}, status=400)
        
        from .models import Product
        from .serializers import ProductSerializer
        
        try:
            products = Product.objects.filter(category_id=category_id)
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

# ✅ ALTERNATIVE: If you want to use PagesAPIViewSet for BlogPage
class BlogPagePagesAPIViewSet(PagesAPIViewSet):
    """Alternative approach using PagesAPIViewSet for BlogPage"""
    
    def get_queryset(self):
        from .models import BlogPage
        return BlogPage.objects.live().public().select_related('category').prefetch_related('blog_authors__author')

    def get_serializer_class(self):
        if self.action == 'list':
            from .serializers import BlogPageListSerializer
            return BlogPageListSerializer
        else:
            from .serializers import CustomBlogPageSerializer
            return CustomBlogPageSerializer