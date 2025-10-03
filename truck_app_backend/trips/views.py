from django.shortcuts import render
# Create your views here.
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from .models import Trip


# --- Helper: scheduling logic ---
def make_schedule(distance_miles, duration_hours, used_hours):
    logs, stops = [], []
    daily_limit = 11  # max driving hours per day
    pickup_time = 1   # hours for pickup
    dropoff_time = 1  # hours for dropoff

    total_hours = duration_hours + pickup_time + dropoff_time
    day = 1
    hours_left = total_hours

    while hours_left > 0:
        drive = min(daily_limit, hours_left)
        stops.append({"day": day, "type": "Driving", "duration": drive})
        logs.append({
            "day": day,
            "driving": drive,
            "rest": 10,
            "fuel": "every 1000 miles"
        })
        hours_left -= drive
        day += 1

    return logs, stops


# --- API Endpoint ---
@api_view(["POST"])
def plan_trip(request):
    """
    Accepts POST JSON:
    {
      "start": {"lat": 40.7128, "lng": -74.0060},
      "pickup": {"lat": 41.8781, "lng": -87.6298},
      "dropoff": {"lat": 34.0522, "lng": -118.2437},
      "hours_used": 5
    }
    """

    try:
        start = request.data["start"]
        pickup = request.data["pickup"]
        dropoff = request.data["dropoff"]
        used_hours = float(request.data.get("hours_used", 0))

        # --- Call ORS Directions API ---
        ors_url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
        headers = {"Authorization": settings.ORS_KEY}
        coords = [
            [start["lng"], start["lat"]],
            [pickup["lng"], pickup["lat"]],
            [dropoff["lng"], dropoff["lat"]],
        ]
        r = requests.post(ors_url, json={"coordinates": coords}, headers=headers)
        r.raise_for_status()
        data = r.json()

        # --- Extract summary info ---
        summary = data["features"][0]["properties"]["summary"]
        distance = summary["distance"] / 1609.34  # meters → miles
        duration = summary["duration"] / 3600     # seconds → hours

        # --- Apply scheduling rules ---
        logs, stops = make_schedule(distance, duration, used_hours)

        print(logs, stops)

        # --- Save trip ---
        trip = Trip.objects.create(
            start=start,
            pickup=pickup,
            dropoff=dropoff,
            hours_used=used_hours,
            route_geojson=data,
            summary={"distance_miles": distance, "duration_hours": duration},
            stops=stops,
            logs=logs
        )

        print("fine")

        # --- Return response ---
        return Response({
            "trip_id": trip.id,
            "route": data,      # GeoJSON for frontend map
            "stops": stops,     # Stops with types/durations
            "logs": logs        # Daily logs for ELD
        })

    except Exception as e:
        return Response({"error": str(e)}, status=400)
