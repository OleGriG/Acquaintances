from django.contrib import admin

from .models import User, Like


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email')


admin.site.register(User, UserAdmin)
admin.site.register(Like)

