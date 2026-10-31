from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0007_remove_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=24, verbose_name='Telefon raqami'),
        ),
    ]
