# Generated by Django 5.1.7 on 2025-04-14 13:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0001_initial"),
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="category",
        ),
        migrations.AddField(
            model_name="product",
            name="category_id",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="catalog.category",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="productimage",
            name="alt_text",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="productimage",
            name="is_primary",
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name="Category",
        ),
    ]
