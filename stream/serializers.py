from rest_framework import serializers
from wagtail.images.models import Image


class StreamSerializer(serializers.Serializer):

    def to_representation(self, value):
        data = value
        enriched_blocks = []
        for block in data:
            block_type = block.block_type
            block_value = block.value
            raw_data = block.block.get_api_representation(block_value, context = self.context )
            
            if block_type == 'card_blocks':
                for card in raw_data.get('card', []):
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
                        'value': raw_data,
                    })

        return enriched_blocks