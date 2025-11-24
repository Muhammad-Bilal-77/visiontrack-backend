from django.contrib import admin
from .models import Employee, Attendance,Feature,SiteSettings,Step

admin.site.register(Employee)
admin.site.register(Attendance)

admin.site.register(Feature)
admin.site.register(SiteSettings)
admin.site.register(Step)