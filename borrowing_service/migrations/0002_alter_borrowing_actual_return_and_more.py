# Generated by Django 5.0.2 on 2024-02-15 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("borrowing_service", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="actual_return",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="expected_return_date",
            field=models.DateField(),
        ),
    ]
