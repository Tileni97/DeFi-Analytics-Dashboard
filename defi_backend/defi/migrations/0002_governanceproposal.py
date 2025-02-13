# Generated by Django 5.1.5 on 2025-02-03 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("defi", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="GovernanceProposal",
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
                ("protocol", models.CharField(max_length=100)),
                ("proposal_id", models.CharField(max_length=50)),
                ("title", models.CharField(max_length=200)),
                ("status", models.CharField(max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
