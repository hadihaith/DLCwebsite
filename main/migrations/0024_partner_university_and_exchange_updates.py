from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0023_exchange_nomination_semester_year"),
    ]

    operations = [
        migrations.AddField(
            model_name="exchangenomination",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="is_exchange_officer",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="PartnerUniversity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150, unique=True)),
                ("logo", models.ImageField(upload_to="partners/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]
