from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0020_exchangeapplication"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExchangeNomination",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                ("institution", models.CharField(max_length=150)),
                ("year_of_study", models.CharField(choices=[("FIRST", "1st Year"), ("SECOND", "2nd Year"), ("THIRD", "3rd Year"), ("FOURTH", "4th Year")], max_length=10)),
                ("degree_level", models.CharField(choices=[("BACHELORS", "Bachelor's"), ("MASTERS", "Master's")], max_length=10)),
                ("completed_credits", models.PositiveIntegerField()),
                ("total_required_credits", models.PositiveIntegerField()),
                ("major", models.CharField(max_length=150)),
                ("completed_semesters", models.PositiveIntegerField(help_text="Number of completed ordinary semesters at the home institution")),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-submitted_at"],
            },
        ),
        migrations.AlterField(
            model_name="exchangeapplication",
            name="intended_term",
            field=models.CharField(choices=[("FALL", "Fall"), ("SPRING", "Spring")], max_length=20),
        ),
    ]
