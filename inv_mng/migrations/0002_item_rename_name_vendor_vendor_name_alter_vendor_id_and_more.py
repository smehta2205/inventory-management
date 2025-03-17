# Generated by Django 5.1.6 on 2025-03-05 20:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inv_mng", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Item",
            fields=[
                ("item_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=200)),
                ("company", models.CharField(max_length=200)),
                ("location", models.CharField(max_length=200)),
                ("iw_unit", models.CharField(max_length=200)),
                ("ow_unit", models.CharField(max_length=200)),
            ],
        ),
        migrations.RenameField(
            model_name="vendor",
            old_name="name",
            new_name="vendor_name",
        ),
        migrations.AlterField(
            model_name="vendor",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name="Stock",
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
                ("expiry_date", models.DateTimeField(blank=True, null=True)),
                ("quantity", models.IntegerField()),
                ("price", models.IntegerField()),
                (
                    "item_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="inv_mng.item"
                    ),
                ),
                (
                    "vendor_name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="inv_mng.vendor"
                    ),
                ),
            ],
        ),
    ]
