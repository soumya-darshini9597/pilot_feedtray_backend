import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Pilot_Feedtray
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["POST"])
def pilot_feedtray_view(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        intial_value = float(data.get("intial_value"))

        # Get latest record
        last_entry = Pilot_Feedtray.objects.order_by('-timestamp').first()

        if not last_entry:
            return JsonResponse({"error": "No base value found in database."}, status=400)

        # Use remaining_value if exists, else base_value
        current_value = float(last_entry.remaining_value) if last_entry.remaining_value else float(last_entry.base_value)

        if intial_value > current_value:
            return JsonResponse({
                "error": "Input exceeds remaining value.",
                "available": current_value
            }, status=400)

        new_remaining = current_value - intial_value

        # Save new record and auto-update base_value = remaining
        new_entry = Pilot_Feedtray.objects.create(
            base_value=str(new_remaining),  # updated base
            intial_value=str(intial_value),
            remaining_value=str(new_remaining),
            cycle_count=last_entry.cycle_count or '1'
        )

        return JsonResponse({
            "message": "Value accepted.",
            "submitted_value": intial_value,
            "new_remaining_base_value": new_remaining
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["GET"])
def get_latest_feedtray_status(request):
    try:
        last_entry = Pilot_Feedtray.objects.order_by('-timestamp').first()

        if not last_entry:
            return JsonResponse({"error": "No data found."}, status=404)

        response_data = {
            "base_value": last_entry.base_value,
            "remaining_value": last_entry.remaining_value,
            "intial_value": last_entry.intial_value,
            "cycle_count": last_entry.cycle_count,
            "timestamp": last_entry.timestamp
        }

        return JsonResponse(response_data, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



@csrf_exempt
def get_base_value(request):
    if request.method == 'GET':
        latest_entry = Pilot_Feedtray.objects.order_by('-timestamp').first()
        if latest_entry:
            return JsonResponse({'base_value': latest_entry.base_value})
        else:
            return JsonResponse({'error': 'No data found'}, status=404)
    return JsonResponse({'error': 'Only GET method allowed'}, status=405)