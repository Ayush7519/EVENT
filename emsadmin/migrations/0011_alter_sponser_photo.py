# Generated by Django 4.2 on 2023-12-10 11:52

from django.db import migrations, models
import emsadmin.models


class Migration(migrations.Migration):
    dependencies = [
        ("emsadmin", "0010_alter_sponser_photo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sponser",
            name="photo",
            field=models.ImageField(
                blank=True, upload_to=emsadmin.models.category_image_dir_path
            ),
        ),
    ]
