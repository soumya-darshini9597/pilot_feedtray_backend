from django.db import models

class Pilot_Feedtray(models.Model):
    id = models.IntegerField(primary_key=True)
    base_value = models.CharField(max_length=250, null=True, blank=True)
    intial_value = models.CharField(max_length=250, null=True, blank=True)
    cycle_count = models.CharField(max_length=250, null=True, blank=True)
    remaining_value = models.CharField(max_length=255, null=True, blank=True) 
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id} {self.base_value} {self.intial_value} {self.cycle_count},{self.remaining_value},{self.timestamp}"

  