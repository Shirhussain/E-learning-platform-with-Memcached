# Generated by Django 3.1.4 on 2020-12-30 16:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_content_file_image_text_video'),
    ]

    operations = [
        migrations.RenameField(
            model_name='module',
            old_name='courses',
            new_name='course',
        ),
    ]
