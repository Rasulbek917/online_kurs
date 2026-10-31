import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0005_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Ism-familiyasi')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='teachers/', verbose_name='Rasmi')),
                ('bio', models.TextField(verbose_name='O‘qituvchi haqida')),
                ('order', models.PositiveIntegerField(default=1, verbose_name='Ko‘rsatish tartibi')),
                ('is_active', models.BooleanField(default=True, verbose_name='Saytda ko‘rsatish')),
                ('categories', models.ManyToManyField(blank=True, related_name='teachers', to='academy.category', verbose_name='Dars beradigan yo‘nalishlar')),
            ],
            options={
                'verbose_name': 'O‘qituvchi',
                'verbose_name_plural': 'O‘qituvchilar',
                'ordering': ['order', 'name'],
            },
        ),
    ]
