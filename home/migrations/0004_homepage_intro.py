# Generated by Django 2.0.4 on 2018-05-05 08:09

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20180426_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='intro',
            field=wagtail.core.fields.RichTextField(blank=True),
        ),
    ]
