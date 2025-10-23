from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0021_exchangenomination"),
    ]

    operations = [
        migrations.RenameField(
            model_name="exchangenomination",
            old_name="email",
            new_name="student_email",
        ),
        migrations.AddField(
            model_name="exchangenomination",
            name="coordinator_email",
            field=models.EmailField(default="exchange@example.com", max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="exchangenomination",
            name="coordinator_name",
            field=models.CharField(default="Exchange Coordinator", max_length=150),
            preserve_default=False,
        ),
    ]
