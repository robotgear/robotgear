# Generated by Django 3.0.4 on 2020-03-19 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0003_auto_20200106_0153'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='secondary_key',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='teams',
            field=models.ManyToManyField(to='teams.Team'),
        ),
        migrations.AlterField(
            model_name='event',
            name='key',
            field=models.TextField(),
        ),
    ]
