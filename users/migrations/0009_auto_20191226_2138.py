# Generated by Django 3.0.1 on 2019-12-26 21:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20190707_2038'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='teammembership',
            unique_together={('user', 'team')},
        ),
    ]