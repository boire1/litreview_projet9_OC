# Generated by Django 4.2.2 on 2023-08-09 12:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("litreviewApp", "0008_ticket_updated_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
