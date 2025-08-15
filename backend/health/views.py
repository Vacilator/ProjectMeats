from django.http import JsonResponse


def health(request):
    # Extend with DB check if desired
    return JsonResponse({"status": "ok"}, status=200)
