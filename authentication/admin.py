from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    ordering = ('email',)
    
    list_display = ('email', 'is_staff', 'is_active')
    
    search_fields = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name')}),
        ('İzinler', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Tarihler', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(User, CustomUserAdmin)