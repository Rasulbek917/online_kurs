from django.db import migrations


def add_backend_category(apps, schema_editor):
    Category = apps.get_model("academy", "Category")
    Category.objects.get_or_create(name="Backend", defaults={"icon": "💻"})


class Migration(migrations.Migration):
    dependencies = [("academy", "0001_initial")]

    operations = [migrations.RunPython(add_backend_category, migrations.RunPython.noop)]
