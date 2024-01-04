# Generated by Django 4.2 on 2023-12-10 15:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("booking", "0004_ticket_booked_by"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ticket",
            name="id",
        ),
        migrations.AlterField(
            model_name="ticket",
            name="ticket_no",
            field=models.AutoField(default=1, primary_key=True, serialize=False),
        ),
    ]