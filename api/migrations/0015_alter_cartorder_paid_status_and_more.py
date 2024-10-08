# Generated by Django 5.0.6 on 2024-08-27 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_alter_product_category_alter_product_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartorder',
            name='paid_status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='cartorder',
            name='product_status',
            field=models.CharField(choices=[('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered')], default='processing', max_length=30),
        ),
    ]
