from django.contrib import admin
from.models import Pilot_Feedtray


@admin.register(Pilot_Feedtray)
class Pilot_FeedtrayAdmin(admin.ModelAdmin):
    list_display=["id","base_value","intial_value","cycle_count","remaining_value","timestamp"]