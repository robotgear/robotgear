from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User, TeamMembership


class MembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 0
    raw_id_fields = ("team", )


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Custom Entries', {'fields': ('email_confirmed', 'zip_code', 'country',
                                                                      'description', 'avatar')}),)
    inlines = [MembershipInline]
    exclude = ('teams',)
