from django.http import JsonResponse


class Json404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404 and request.headers.get("accept") == "application/json":
            return JsonResponse({"error": "Not found."}, status=404)
        return response
