# Generated by Django 5.1.5 on 2025-02-08 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defi', '0009_remove_yielddata_protocol_remove_yielddata_tvl_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='yielddata',
            name='apyReward',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
