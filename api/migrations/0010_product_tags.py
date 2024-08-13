# Generated by Django 5.0.6 on 2024-08-13 12:30

import taggit.managers
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_rename_delivery_time_vendor_shipping_on_time'),
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
