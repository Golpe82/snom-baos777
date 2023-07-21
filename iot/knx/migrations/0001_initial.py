from django.db import migrations
from django.contrib.auth.models import User
from django.conf import settings


def _create_super_user(
    apps,
    schema_editor,
    username="admin",
    password="admin",
    email="admin@admin.com",
    firstName="admin",
    lastName="admin",
):
    invalidInputs = ["", None]

    if username.strip() in invalidInputs or password.strip() in invalidInputs:
        return None

    user = User(
        username=username,
        email=email,
        first_name=firstName,
        last_name=lastName,
    )
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()

    return user


def _create_user_if_not_extists(apps, schema_editor):
    if not User.objects.count():
        _create_super_user(apps, schema_editor)


class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunPython(_create_user_if_not_extists),
        ]
