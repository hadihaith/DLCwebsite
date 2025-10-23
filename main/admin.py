from django.contrib import admin
from .models import Application, ExchangeApplication, ExchangeNomination, PartnerUniversity, ParkingApplication, ExchangeProgramSettings, User, DeanListStudent, DeanList, Event, Attendance, EventSection

# Register your models here.
admin.site.register(Application)
admin.site.register(ExchangeApplication)
admin.site.register(ExchangeNomination)
admin.site.register(PartnerUniversity)
admin.site.register(ParkingApplication)
admin.site.register(ExchangeProgramSettings)
admin.site.register(User)
admin.site.register(DeanList)
admin.site.register(DeanListStudent)
admin.site.register(Event)
admin.site.register(EventSection)
admin.site.register(Attendance)

