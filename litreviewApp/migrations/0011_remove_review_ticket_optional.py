# Generated by Django 4.2.2 on 2023-08-21 18:33

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("litreviewApp", "0010_review_ticket_optional"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="review",
            name="ticket_optional",
        ),
    ]
