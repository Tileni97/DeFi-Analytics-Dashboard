# Generated by Django 5.1.5 on 2025-02-03 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("defi", "0005_riskmetric_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="riskmetric",
            name="health_score",
            field=models.FloatField(default=0),
        ),
    ]
