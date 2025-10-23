from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0022_update_exchange_nomination_contacts"),
    ]

    operations = [
        migrations.AddField(
            model_name="exchangenomination",
            name="academic_year",
            field=models.CharField(
                default="2025/2026",
                help_text="Academic year in YYYY/YYYY format",
                max_length=9,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="exchangenomination",
            name="semester_to_apply_for",
            field=models.CharField(
                choices=[("FALL", "Fall"), ("SPRING", "Spring"), ("SUMMER", "Summer")],
                default="FALL",
                max_length=10,
            ),
            preserve_default=False,
        ),
    ]
