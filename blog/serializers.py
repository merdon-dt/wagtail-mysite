import re
from rest_framework import serializers
from wagtail.images.api.fields import ImageRenditionField
from wagtail.images.models import Image

class BlogDetailsPageSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    title= serializers.CharField()
    blog_title= serializers.CharField()
    slug= serializers.CharField()
    content= serializers.JSONField()
    # date_created= serializers.DateTimeField()
    # date_updated= serializers.DateTimeField()
    blog_image = ImageRenditionField('fill-800x400',)
    
    
    # def to_representation(self, instance):
    #     print("📦 Object:", model_to_dict(instance))
    #     return super().to_representation(instance)

    # def get_tags(self, obj):
    #     return [tag.name for tag in obj.tags.all()]

    # def get_categories(self, obj):
    #     return [cat.name for cat in obj.categories.all()]

    # def get_authors(self, obj):
    #     return [author.author_name for author in obj.author_tags.all()]
    
        
    def to_representation(self, instance):
        data = super().to_representation(instance)

        print("\n🔍 START SERIALIZER FOR:", instance)
        print("📦 Initial data:", data)

        enriched_blocks = []

        # Loop through each block in the StreamField
        for block in instance.content:  # block is a StreamChild
            print("\n🧩 New block:")
            print("🔹 Raw block:", block)

            block_type = block.block_type
            value = block.value

            print("🔸 Block type:", block_type)
            print("🔸 Raw block value:", value)

            # Convert StructValue or ListValue into a plain Python dict
            try:
                raw_value = block.block.get_api_representation(value, context=self.context)
                print("✅ Converted value to API-safe dict:", raw_value)
            except Exception as e:
                print("❌ Failed to convert value to dict:", e)
                raw_value = value  # fallback (may cause errors if not serializable)

            # Handle card_blocks (List of cards with image)
            if block_type == "card_blocks":
                print("📦 Handling card_blocks")
                for card in raw_value.get("card", []):
                    print("🃏 Card:", card)
                    image_id = card.get("image")
                    print("🖼️ Card image ID:", image_id)

                    if image_id:
                        try:
                            image = Image.objects.get(id=image_id)
                            print("✅ Found image:", image)
                            rendition = image.get_rendition("fill-800x400")
                            print("✅ Got rendition:", rendition.url)

                            card["image"] = {
                                "url": rendition.url,
                                "alt": image.title,
                            }
                        except Exception as e:
                            print("❌ Error processing image:", e)
                            card["image"] = None

            # Handle CTA block (one image)
            elif block_type == "cta_blocks":
                print("📦 Handling cta_blocks")
                image_id = raw_value.get("image")
                print("🖼️ CTA image ID:", image_id)

                if image_id:
                    try:
                        image = Image.objects.get(id=image_id)
                        print("✅ Found image:", image)
                        rendition = image.get_rendition("fill-800x400")
                        print("✅ Got rendition:", rendition.url)

                        raw_value["image"] = {
                            "url": rendition.url,
                            "alt": image.title,
                        }
                    except Exception as e:
                        print("❌ Error processing CTA image:", e)
                        raw_value["image"] = None

            enriched_block = {
                "type": block_type,
                "value": raw_value
            }
            print("✅ Final enriched block:", enriched_block)

            enriched_blocks.append(enriched_block)

        # Replace content with enriched version
        data["content"] = enriched_blocks
        print("\n✅ Final serialized data for blog post:", data)
        return data
            
            
class TagSerializer(serializers.Serializer):
    def to_representation(self, value):
        tag_names = [tag.name for tag in value]
        return tag_names
    
class CategorySerializer(serializers.Serializer):
    def to_representation(self, value):
        cat_names = [cat.name for cat in value]
        return cat_names    
    
# class AuthorTagSerializer(serializers.Serializer):
#     def to_representation(self, value):
#        author_details = [{
#             "author_name": author.author_name,
#             "author_website": author.author_website,
#             "author_image": author.author_image,
#         } for author in value]    
#        return author_details