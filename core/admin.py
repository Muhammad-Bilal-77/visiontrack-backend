from django.contrib import admin
from .models import Employee, Attendance,Feature,SiteSettings,Step

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'user', 'image')
    list_filter = ('user__role',)
    
    def get_name(self, obj):
        return obj.name
    get_name.short_description = 'Name'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter user dropdown to show only employees."""
        if db_field.name == "user":
            kwargs["queryset"] = db_field.related_model.objects.filter(role='employee')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Attendance)

admin.site.register(Feature)
admin.site.register(SiteSettings)
admin.site.register(Step)