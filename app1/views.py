import csv
import json
from django.db import models
from .models import Pilot_Feedtray
from django.http import JsonResponse
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.utils.timezone import make_aware, get_current_timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods





@csrf_exempt
@require_http_methods(["POST"])
def pilot_feedtray_view(request):
    try:
        data = json.loads(request.body.decode("utf-8"))

        mqtt_value = data.get("mqtt_value")
        usage_value = data.get("value")

        last_entry = Pilot_Feedtray.objects.order_by('-timestamp').first()

        #Start new cycle if MQTT value is posted
        if mqtt_value is not None:
            mqtt_value = float(mqtt_value)

            # Allow new cycle only if remaining is effectively 0
            if not last_entry or float(last_entry.remaining_value or 0) <= 0.0001:
                new_entry = Pilot_Feedtray.objects.create(
                    base_value=str(mqtt_value),
                    intial_value=str(mqtt_value),  # Consider renaming to initial_value if typo
                    remaining_value=str(mqtt_value),
                    cycle_count="1",
                    cycle_value="Cycle 1"
                )
                return JsonResponse({
                    "message": "New cycle started.",
                    "base_value": new_entry.base_value
                })

            else:
                return JsonResponse({
                    "error": "Cycle not complete. Wait until remaining_value = 0."
                }, status=400)

        #Usage deduction
        elif usage_value is not None:
            usage_value = float(usage_value)

            if not last_entry:
                return JsonResponse({"error": "No existing cycle found. Start with mqtt_value."}, status=400)

            prev_remaining = float(last_entry.remaining_value or 0)
            base_value = float(last_entry.base_value or 0)

            if usage_value > prev_remaining:
                return JsonResponse({
                    "error": "Usage exceeds remaining value.",
                    "available": prev_remaining
                }, status=400)

            new_remaining = prev_remaining - usage_value

            new_entry = Pilot_Feedtray.objects.create(
                base_value=str(base_value),
                intial_value=str(prev_remaining),
                remaining_value=str(new_remaining),
                cycle_count=str(int(last_entry.cycle_count or "0") + 1),
                cycle_value=str(usage_value)
            )

            return JsonResponse({
                "message": "Usage recorded.",
                "used": usage_value,
                "base_value": base_value,
                "initial_value": prev_remaining,
                "remaining_value": new_remaining,
                "cycle_value": usage_value
            })

        else:
            return JsonResponse({"error": "Send either mqtt_value or value"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)





#new modification
@csrf_exempt
@require_http_methods(["GET"])
def get_recent_cycle_data(request):
    try:
        # Get the most recent "reset" row (start of new cycle)
        latest_starter = (
            Pilot_Feedtray.objects
            .filter(cycle_count=0)
            .exclude(intial_value__isnull=True)
            .exclude(intial_value='')
            .order_by('-timestamp')
            .first()
        )

        if not latest_starter:
            return JsonResponse({"message": "No base value row found."}, status=404)

        # Get only records from that reset timestamp onward
        records = Pilot_Feedtray.objects.filter(
            timestamp__gte=latest_starter.timestamp
        ).order_by('timestamp')

        response = []
        for record in records:
            response.append({
                "base_value": str(record.base_value),
                "intial_value": str(record.intial_value),
                "remaining_value": str(record.remaining_value),
                "cycle_count": record.cycle_count,
                "cycle_value": str(record.cycle_value) if record.cycle_value else "0",
                "timestamp": record.timestamp.isoformat(),
            })

        return JsonResponse({"data": response}, status=200)

    except Exception as e:
        # Capture full error message
        return JsonResponse({"error": str(e)}, status=500)





@csrf_exempt
@require_http_methods(["GET"])
def filter_feedtray_data(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')  

    # Validate both dates exist
    if not start_date or not end_date:
        return JsonResponse({"error": "Both 'start_date' and 'end_date' are required in format YYYY-MM-DD."}, status=400)

    try:
        # Parse and make datetimes timezone-aware
        start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))  # include entire end day
    except ValueError:
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    # Filter queryset
    filtered_data = Pilot_Feedtray.objects.filter(timestamp__range=(start_date, end_date)).order_by('timestamp')

    # Serialize result
    response = [
        {
            "base_value": record.base_value,
            "intial_value": record.intial_value,
            "remaining_value": record.remaining_value,
            "cycle_count": record.cycle_count,
            "timestamp": record.timestamp.isoformat()
        } for record in filtered_data
    ]

    return JsonResponse({"data": response}, status=200)





@csrf_exempt
@require_http_methods(["GET"])
def download_feedtray_data(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        return JsonResponse({"error": "start_date and end_date are required."}, status=400)

    try:
        # Make timezone-aware datetimes in UTC
        start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
    except ValueError:
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    records = Pilot_Feedtray.objects.filter(timestamp__range=(start_date, end_date)).order_by('timestamp')

    # Prepare CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pilot_feedtray_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Base Value', 'Initial Value', 'Remaining Value', 'Cycle Count', 'Cycle Value', 'Timestamp'])

    # Convert UTC -> IST
    local_tz = get_current_timezone()

    for record in records:
        local_timestamp = record.timestamp.astimezone(local_tz)
        writer.writerow([
            record.base_value,
            record.intial_value,
            record.remaining_value,
            record.cycle_count,
            record.cycle_value,
            local_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    return response