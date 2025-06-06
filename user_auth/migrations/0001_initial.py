# Generated by Django 5.1.7 on 2025-06-01 15:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LoginHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("token_ref", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "device_name",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True, null=True)),
                ("login_date", models.DateTimeField(auto_now_add=True)),
                ("logout_date", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_auth_login_histories",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "user_auth_loginhistory",
            },
        ),
        migrations.CreateModel(
            name="UserToken",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("token", models.CharField(max_length=255, unique=True)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("expired_date", models.DateTimeField()),
                (
                    "device_name",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_auth_tokens",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "user_auth_usertoken",
            },
        ),
    ]
