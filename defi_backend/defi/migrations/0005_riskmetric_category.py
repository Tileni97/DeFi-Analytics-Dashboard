# Generated by Django 5.1.5 on 2025-02-03 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("defi", "0004_alter_riskmetric_dominance_ratio_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="riskmetric",
            name="category",
            field=models.CharField(default="Other", max_length=50),
        ),
    ]
