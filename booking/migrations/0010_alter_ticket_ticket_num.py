# Generated by Django 4.2 on 2023-12-11 17:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("booking", "0009_rename_ticket_no_ticket_ticket_id_ticket_ticket_num"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ticket",
            name="ticket_num",
            field=models.CharField(blank=True, max_length=10000),
        ),
    ]