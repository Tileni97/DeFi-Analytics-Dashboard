# Generated by Django 5.1.5 on 2025-02-09 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defi', '0015_alter_riskscore_risk_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='riskscore',
            name='audit_status',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='riskscore',
            name='protocol',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='riskscore',
            name='risk_score',
            field=models.FloatField(default=0.0),
        ),
    ]
