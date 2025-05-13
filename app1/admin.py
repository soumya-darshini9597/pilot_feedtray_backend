from django.contrib import admin
from.models import Pilot_Feedtray


@admin.register(Pilot_Feedtray)
class Pilot_FeedtrayAdmin(admin.ModelAdmin):
    list_display=["base_value","intial_value","cycle_value","cycle_count","remaining_value","timestamp"]