from django.db import models
import json

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
