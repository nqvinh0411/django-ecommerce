# Generated by Django 5.1.7 on 2025-04-15 15:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0003_remove_product_seller_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="category_id",
            new_name="category",
        ),
    ]
