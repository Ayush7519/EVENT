# Generated by Django 4.2 on 2024-02-24 04:17

from django.db import migrations, models
import emsadmin.models


class Migration(migrations.Migration):
    dependencies = [
        ("emsadmin", "0035_alter_sponser_photo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sponser",
            name="photo",
            field=models.ImageField(upload_to=emsadmin.models.category_image_dir_path),
        ),
    ]