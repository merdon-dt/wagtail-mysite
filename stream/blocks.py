from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class TextAndTitleBlocks(blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text='Add a title')
    text = blocks.TextBlock(required=True, help_text='Add some text')
    
    class Meta:
        template = 'stream/text_and_title.html'
        icon = 'edit'
        label = 'Text and Title'
        
class CardBlocks(blocks.StructBlock):
    
    title = blocks.CharBlock(required=True, help_text='Add a title')
    card = blocks.ListBlock(
         blocks.StructBlock([
        ('image', ImageChooserBlock(required=True)),
        ('title', blocks.CharBlock(required=True)),
        ('text', blocks.TextBlock(required=True)),
        ('button_page', blocks.PageChooserBlock(required=False)),
        ('button_url', blocks.URLBlock(required=False, help_text = 'Add a link if needed'))
    ])
    )
    class Meta:  # noqa
        template = 'stream/card_block.html'
        icon = 'edit'
        label = 'Card'
        
class RichTextBlocks(blocks.RichTextBlock):
    
    class Meta:  # noqa
        template = 'stream/rich_text_block.html'
        icon = 'doc-full'
        label = 'Rich Text'
        
class SimpleRichTextBlocks(blocks.RichTextBlock):
    
    def __init__(self, **kwargs):
        super().__init__(features=['bold', 'italic', 'link'], **kwargs)
    
    class Meta:  # noqa
        template = 'stream/rich_text_block.html'
        icon = 'edit'
        label = 'Simple Text'