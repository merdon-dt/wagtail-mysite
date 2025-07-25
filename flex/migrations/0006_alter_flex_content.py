# Generated by Django 5.2.1 on 2025-06-06 10:21

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flex', '0005_alter_flex_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flex',
            name='content',
            field=wagtail.fields.StreamField([('text_and_title', 2), ('rich_text', 3), ('simple_text', 4), ('card_blocks', 12), ('cta_blocks', 17), ('button_blocks', 19)], blank=True, block_lookup={0: ('wagtail.blocks.CharBlock', (), {'help_text': 'Add a title', 'required': True}), 1: ('wagtail.blocks.TextBlock', (), {'help_text': 'Add some text', 'required': True}), 2: ('wagtail.blocks.StructBlock', [[('title', 0), ('text', 1)]], {}), 3: ('stream.blocks.RichTextBlocks', (), {}), 4: ('stream.blocks.SimpleRichTextBlocks', (), {}), 5: ('wagtail.images.blocks.ImageChooserBlock', (), {'required': True}), 6: ('wagtail.blocks.CharBlock', (), {'required': True}), 7: ('wagtail.blocks.TextBlock', (), {'required': True}), 8: ('wagtail.blocks.PageChooserBlock', (), {'required': False}), 9: ('wagtail.blocks.URLBlock', (), {'help_text': 'Add a link if needed', 'required': False}), 10: ('wagtail.blocks.StructBlock', [[('image', 5), ('title', 6), ('text', 7), ('button_page', 8), ('button_url', 9)]], {}), 11: ('wagtail.blocks.ListBlock', (10,), {}), 12: ('wagtail.blocks.StructBlock', [[('title', 0), ('card', 11)]], {}), 13: ('wagtail.blocks.RichTextBlock', (), {'max_length': 60, 'null': True, 'required': True}), 14: ('wagtail.blocks.TextBlock', (), {'max_length': 260, 'null': True, 'required': True}), 15: ('wagtail.blocks.PageChooserBlock', (), {'help_text': 'Add a link if needed', 'required': False}), 16: ('wagtail.blocks.CharBlock', (), {'default': 'Read More', 'required': False}), 17: ('wagtail.blocks.StructBlock', [[('title', 13), ('text', 14), ('button_page', 15), ('button_url', 9), ('button_text', 16)]], {}), 18: ('wagtail.blocks.PageChooserBlock', (), {'help_text': 'Add a page url, If added it would be primary button', 'required': False}), 19: ('wagtail.blocks.StructBlock', [[('page_url', 18), ('page_link', 9)]], {})}, default=list),
        ),
    ]
