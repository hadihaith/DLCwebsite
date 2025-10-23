from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0019_eventsection_attendance_sections"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExchangeApplication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("home_university", models.CharField(max_length=150)),
                ("home_country", models.CharField(max_length=100)),
                ("study_level", models.CharField(choices=[("UNDERGRADUATE", "Undergraduate"), ("GRADUATE", "Graduate")], max_length=20)),
                ("intended_term", models.CharField(choices=[("FALL", "Fall"), ("SPRING", "Spring"), ("SUMMER", "Summer")], max_length=20)),
                ("intended_year", models.PositiveIntegerField()),
                ("major_interest", models.CharField(max_length=120)),
                ("current_gpa", models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ("english_proficiency", models.CharField(blank=True, max_length=100)),
                ("accommodation_required", models.BooleanField(default=False)),
                ("additional_information", models.TextField(blank=True)),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-submitted_at"],
            },
        ),
    ]
