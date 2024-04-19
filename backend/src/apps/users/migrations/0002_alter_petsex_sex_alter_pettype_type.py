# Generated by Django 5.0.4 on 2024-04-19 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="petsex",
            name="sex",
            field=models.CharField(
                db_column="sex", max_length=50, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="pettype",
            name="type",
            field=models.CharField(
                db_column="type", max_length=50, unique=True
            ),
        ),
    ]
