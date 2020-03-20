from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path

from django_q.tasks import async_task

from teams.models import Competition, Team
from teams.tasks import update_current_year_FIRST


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'full_name')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    change_list_template = "admin/competition_changelist.html"
    list_display = ('team_name_w_comp', 'nickname')
    search_fields = ('team_num', 'nickname')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('update/<str:comp>/', self.FIRST_update)
        ]
        return my_urls + urls

    def FIRST_update(self, request, comp):
        if comp == "all":
            update_current_year_FIRST()
        elif comp == "history":
            async_task('teams.tasks.update_all_FIRST')
        else:
            update_current_year_FIRST(comp)
        return redirect("admin:teams_team_changelist")
