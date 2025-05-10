import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Pilot_Feedtray


@csrf_exempt
def pilot_feedtray_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))

        if 'value' not in payload:
            return JsonResponse({'error': 'Missing "value" in payload'}, status=400)

        input_value = float(payload['value'])

        last_entry = Pilot_Feedtray.objects.order_by('-timestamp').first()

        # Case 1: No previous entry or remaining = 0 → Start new cycle
        if last_entry is None or float(last_entry.remaining_value or last_entry.base_value) == 0:
            if 'base_value' not in payload:
                return JsonResponse({'error': 'New cycle requires "base_value"'}, status=400)

            base_value = float(payload['base_value'])
            remaining_value = base_value - input_value

            if remaining_value < 0:
                return JsonResponse({
                    'error': 'Input value exceeds base value',
                    'available_base_value': base_value
                }, status=400)

            Pilot_Feedtray.objects.create(
                base_value=str(base_value),
                intial_value=str(input_value),
                remaining_value=str(remaining_value),
                cycle_count='1'
            )
            return JsonResponse({
                'message': 'New cycle started',
                'remaining_value': remaining_value
            })

        # Case 2: Continuing previous cycle
        prev_remaining = float(last_entry.remaining_value)

        if input_value > prev_remaining:
            return JsonResponse({
                'error': 'Input value exceeds remaining value ',
                'available_base_value': float(last_entry.base_value),
                'remaining_value': prev_remaining
            }, status=400)

        remaining_value = prev_remaining - input_value

        # When remaining becomes 0 after this POST, we expect next base to be posted in the next request
        Pilot_Feedtray.objects.create(
            base_value=last_entry.base_value,
            intial_value=str(input_value),
            remaining_value=str(remaining_value),
            cycle_count=last_entry.cycle_count
        )
        return JsonResponse({
            'message': 'Value processed',
            'remaining_value': remaining_value
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




@csrf_exempt
def get_base_value(request):
    if request.method == 'GET':
        latest_entry = Pilot_Feedtray.objects.order_by('-timestamp').first()
        if latest_entry:
            return JsonResponse({'base_value': latest_entry.base_value})
        else:
            return JsonResponse({'error': 'No data found'}, status=404)
    return JsonResponse({'error': 'Only GET method allowed'}, status=405)