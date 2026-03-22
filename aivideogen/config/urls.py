from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from generator.views import serve_video

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve_video),
    path('admin/', admin.site.urls),
    path('', include('generator.urls')),
    path('researcher/', include('researcher.urls')),
]
