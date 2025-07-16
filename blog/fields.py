# blog/fields.py
from rest_framework.fields import Field

class ImageSerializerField(Field):
    def to_representation(self, value):
        return {
            "url": value.file.url,
            "title": value.title,
            "width": value.width,
            "height": value.height
        }
