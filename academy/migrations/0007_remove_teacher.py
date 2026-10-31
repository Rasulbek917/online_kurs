from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0006_teacher'),
    ]

    operations = [
        migrations.DeleteModel(name='Teacher'),
    ]
