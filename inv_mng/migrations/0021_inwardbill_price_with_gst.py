# Generated by Django 5.1.6 on 2025-03-27 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inv_mng", "0020_inwardbill_is_paid"),
    ]

    operations = [
        migrations.AddField(
            model_name="inwardbill",
            name="price_with_gst",
            field=models.BooleanField(default=False),
        ),
    ]
