from django.contrib import admin
from .models import Asset, Music, VideoProject, YouTubeToken

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at')

@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at')

@admin.register(VideoProject)
class VideoProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    list_filter = ('status', 'engine')

@admin.register(YouTubeToken)
class YouTubeTokenAdmin(admin.ModelAdmin):
    list_display = ('updated_at',)
