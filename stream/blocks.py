from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.blocks.struct_block import StructValue



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
        

class CTABlock(blocks.StructBlock):
    title = blocks.RichTextBlock(required=True, max_length=60, null=True,)
    text = blocks.TextBlock(required=True, max_length=260, null=True)
    button_page = blocks.PageChooserBlock(required=False, help_text = 'Add a link if needed')
    button_url = blocks.URLBlock(required=False, help_text = 'Add a link if needed')
    button_text = blocks.CharBlock(required=False, default='Read More')
    
    class Meta:  # noqa
        template = 'stream/cta_block.html'
        icon = 'edit'
        label = 'Call to Action'  

        
class LinkStructBlock(StructValue):
    
    def url(self):
        page = self.get('page_url')
        external_url = self.get('page_link')
        if page:
            print("the page url is", page)
            return page.url
        elif external_url:
            print("the page url is", external_url)
            return external_url
        return None
    def title(self):
        page = self.get('page_url')
        external_url = self.get('page_link')
        if page:
            return page.title
        elif external_url:
            return external_url  # or you can return a hardcoded label like "External Link"
        return "Untitled"

class SingleButtonBlock(blocks.StructBlock):
    
    page_url = blocks.PageChooserBlock(required=False, help_text = 'Add a page url, If added it would be primary button')             
    page_link = blocks.URLBlock(required=False, help_text = 'Add a link if needed')
    
    class Meta: #noqa
        template = 'stream/single_button_block.html'
        icon = 'button'
        label = 'Single Button'
        value_class = LinkStructBlock