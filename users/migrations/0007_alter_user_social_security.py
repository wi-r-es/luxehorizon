# Generated by Django 4.2.17 on 2025-01-10 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_user_social_security'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='social_security',
            field=models.IntegerField(null=True),
        ),
    ]
