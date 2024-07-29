from django.contrib import admin
from .models import CustomUser

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email',"id", 'username', 'role', 'is_active', 'is_admin']

admin.site.register(CustomUser,CustomUserAdmin)