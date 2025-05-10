from django.db import models


class Pilot_Feedtray(models.Model):
    # id = models.IntegerField(primary_key=True)
    base_value = models.CharField(max_length=250, null=True, blank=True)
    intial_value = models.CharField(max_length=250, null=True, blank=True)
    cycle_count = models.CharField(max_length=250, null=True, blank=True,default='0')
    remaining_value = models.CharField(max_length=255, null=True, blank=True)
    cycle_value = models.CharField(max_length=250, null=True, blank=True)  # New field for cycle value
    timestamp = models.DateTimeField(auto_now_add=True)

    