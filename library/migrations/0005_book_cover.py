# Generated by Django 4.1.1 on 2022-09-20 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0004_author_description_alter_book_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cover',
            field=models.ImageField(null=True, upload_to='covers', verbose_name='Viršelis'),
        ),
    ]