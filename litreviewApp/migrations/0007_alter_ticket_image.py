# Generated by Django 4.2.2 on 2023-07-20 22:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("litreviewApp", "0006_ticketreviewresponse"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ticket",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="ticket_images/"),
        ),
    ]