from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academy", "0003_lessonquestion"),
    ]

    operations = [
        migrations.AddField(
            model_name="lessonquestion",
            name="image",
            field=models.ImageField(blank=True, help_text="Savolga tegishli rasmni ixtiyoriy yuklang.", null=True, upload_to="questions/", verbose_name="Savol rasmi"),
        ),
    ]
