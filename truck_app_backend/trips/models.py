from django.db import models
import json
from django.utils import timezone

# Create your models here.
class Trip(models.Model):
    start = models.JSONField()
    pickup = models.JSONField()
    dropoff = models.JSONField()
    hours_used = models.FloatField()
    route_geojson = models.JSONField()
    summary = models.JSONField()
    stops = models.JSONField()
    logs = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Trip {self.id}: {self.start} → {self.dropoff}"

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('driving', 'Driving'),
        ('fueling', 'Fueling'),
        ('rest', 'Rest'),
    ]
    
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    day_number = models.IntegerField()
    duration = models.IntegerField()  # Duration in seconds
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    def __str__(self):
        return f"{self.name} activity for Trip {self.trip.id} on Day {self.day_number}"
