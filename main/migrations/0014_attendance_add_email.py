# Generated manual migration to add email field to Attendance
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_event_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
    ]
