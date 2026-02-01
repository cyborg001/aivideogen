import time
from .views import update_last_activity

class ActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Update activity timestamp on every request
        # This prevents auto-shutdown during manual navigation
        update_last_activity()
        
        response = self.get_response(request)
        return response
