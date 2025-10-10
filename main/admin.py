from django.contrib import admin
from .models import Application, User, DeanListStudent, DeanList, Event, Attendance, EventSection

# Register your models here.
admin.site.register(Application)
admin.site.register(User)
admin.site.register(DeanList)
admin.site.register(DeanListStudent)
admin.site.register(Event)
admin.site.register(EventSection)
admin.site.register(Attendance)

