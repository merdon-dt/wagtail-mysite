from wagtail.images.models import Image
from rest_framework import serializers

class SimpleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'title', 'width', 'height', 'file']  # or 'file.url' if needed

    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        return obj.file.url if obj.file else None


class ProductImageSerializer(serializers.ModelSerializer):
    product_image = SimpleImageSerializer()

    class Meta:
        model = 'product.ProductImage'
        fields = ['id', 'product_image']
