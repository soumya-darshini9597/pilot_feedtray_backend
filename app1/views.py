import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Pilot_Feedtray
from django.views.decorators.http import require_http_methods

# @csrf_exempt
# @require_http_methods(["POST"])
# def pilot_feedtray_view(request):
#     try:
#         data = json.loads(request.body.decode('utf-8'))
#         intial_value = float(data.get("value"))

#         # Get latest record
#         last_entry = Pilot_Feedtray.objects.order_by('-timestamp').first()

#         if not last_entry:
#             return JsonResponse({"error": "No base value found in database."}, status=400)

#         # Use remaining_value if exists, else base_value
#         current_value = float(last_entry.remaining_value) if last_entry.remaining_value else float(last_entry.base_value)

#         if intial_value > current_value:
#             return JsonResponse({
#                 "error": "Input exceeds remaining value.",
#                 "available": current_value
#             }, status=400)

#         new_remaining = current_value - intial_value

#         # Save new record and auto-update base_value = remaining
#         new_entry = Pilot_Feedtray.objects.create(
#             base_value=str(new_remaining),  # updated base
#             intial_value=str(intial_value),
#             remaining_value=str(new_remaining),
#             cycle_count=last_entry.cycle_count or '1'
#         )

#         return JsonResponse({
#             "message": "Value accepted.",
#             "submitted_value": intial_value,
#             "new_remaining_base_value": new_remaining
#         }, status=200)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


# @csrf_exempt
# @require_http_methods(["POST"])
# def pilot_feedtray_view(request):
#     try:
#         data = json.loads(request.body.decode("utf-8"))

#         mqtt_value = data.get("mqtt_value")
#         usage_value = data.get("value")

#         last_entry = Pilot_Feedtray.objects.order_by('-timestamp').first()

#         # 🟢 New cycle via MQTT
#         if mqtt_value is not None:
#             mqtt_value = float(mqtt_value)

#             # Start new cycle only if last cycle is complete (remaining_value = 0)
#             if not last_entry or float(last_entry.remaining_value or 0) == 0:
#                 Pilot_Feedtray.objects.create(
#                     base_value=str(mqtt_value),
#                     intial_value=str(mqtt_value),
#                     remaining_value=str(mqtt_value),  # Initially, remaining_value = base_value
#                     cycle_count="1"  # Starting the first cycle
#                 )
#                 return JsonResponse({
#                     "message": "New cycle started.",
#                     "base_value": mqtt_value
#                 })

#             else:
#                 return JsonResponse({
#                     "error": "Cycle not complete. Wait until remaining_value = 0."
#                 }, status=400)

#         # 🔵 Deduction
#         elif usage_value is not None:
#             usage_value = float(usage_value)

#             if not last_entry:
#                 return JsonResponse({"error": "No existing cycle found. Start with mqtt_value."}, status=400)

#             prev_remaining = float(last_entry.remaining_value or 0)
#             base_value = float(last_entry.base_value or 0)

#             # Check if usage exceeds remaining_value
#             if usage_value > prev_remaining:
#                 return JsonResponse({
#                     "error": "Usage exceeds remaining value.",
#                     "available": prev_remaining
#                 }, status=400)

#             new_remaining = prev_remaining - usage_value

#             # Save new entry with updated remaining_value and cycle_count
#             Pilot_Feedtray.objects.create(
#                 base_value=str(base_value),              # keep constant base_value
#                 intial_value=str(prev_remaining),        # initial_value = previous remaining
#                 remaining_value=str(new_remaining),      # updated remaining_value after deduction
#                 cycle_count=str(int(last_entry.cycle_count or "0") + 1)  # Increment cycle count
#             )

#             return JsonResponse({
#                 "message": "Usage recorded.",
#                 "used": usage_value,
#                 "base_value": base_value,
#                 "initial_value": prev_remaining,
#                 "remaining_value": new_remaining
#             })

#         else:
#             return JsonResponse({"error": "Send either mqtt_value or value"}, status=400)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def pilot_feedtray_view(request):
    try:
        data = json.loads(request.body.decode("utf-8"))

        mqtt_value = data.get("mqtt_value")
        usage_value = data.get("value")  # Usage value from the POST request

        last_entry = Pilot_Feedtray.objects.order_by('-timestamp').first()

        # 🟢 New cycle via MQTT
        if mqtt_value is not None:
            mqtt_value = float(mqtt_value)

            if not last_entry or float(last_entry.remaining_value or 0) == 0:
                Pilot_Feedtray.objects.create(
                    base_value=str(mqtt_value),
                    intial_value=str(mqtt_value),
                    remaining_value=str(mqtt_value),
                    cycle_count="1",
                    cycle_value="Cycle 1"  # Example cycle value
                )
                return JsonResponse({
                    "message": "New cycle started.",
                    "base_value": mqtt_value
                })

            else:
                return JsonResponse({
                    "error": "Cycle not complete. Wait until remaining_value = 0."
                }, status=400)

        # 🔵 Deduction and update cycle_value
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

            # Set cycle_value to the usage_value that is posted
            cycle_value = str(usage_value)

            Pilot_Feedtray.objects.create(
                base_value=str(base_value),              # keep constant base
                intial_value=str(prev_remaining),        # initial = previous remaining
                remaining_value=str(new_remaining),      
                cycle_count=str(int(last_entry.cycle_count or "0") + 1),
                cycle_value=cycle_value  

            )

            return JsonResponse({
                "message": "Usage recorded.",
                "used": usage_value,
                "base_value": base_value,
                "initial_value": prev_remaining,
                "remaining_value": new_remaining,
                "cycle_value": cycle_value  
            })

        else:
            return JsonResponse({"error": "Send either mqtt_value or value"}, status=400)

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