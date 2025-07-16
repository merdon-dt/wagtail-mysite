from rest_framework import serializers
from wagtail.images.models import Image

class StreamFieldSerializer(serializers.Serializer):
    def to_representation(self, value):
        enriched_blocks = []
        

        for block in value:  # value is StreamValue
            block_type = block.block_type
            raw_value = block.block.get_api_representation(block.value, context=self.context)

            # handle card block image enrichment
            if block_type == 'card_blocks':
                for card in raw_value.get('card', []):
                    image_id = card.get('image')
                    if image_id:
                        try:
                            image = Image.objects.get(id=image_id)
                            rendition = image.get_rendition('fill-800x400')
                            card['image'] = {
                                'url': rendition.url,
                                'alt': image.title,
                            }
                        except Exception:
                            card['image'] = None

            enriched_blocks.append({
                'type': block_type,
                'value': raw_value,
            })

        return enriched_blocks
