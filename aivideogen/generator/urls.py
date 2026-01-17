from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_project, name='create_project'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/stop/', views.stop_project, name='stop_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/upload/', views.upload_asset, name='upload_asset'),
    path('assets/<int:asset_id>/delete/', views.delete_asset, name='delete_asset'),
    path('api/browse/', views.browse_script, name='browse_script'),
    path('youtube/authorize/', views.youtube_authorize, name='youtube_authorize'),
    path('youtube/callback/', views.youtube_callback, name='youtube_callback'),
    path('project/<int:project_id>/youtube-upload/', views.upload_to_youtube_view, name='youtube_upload'),
    path('music/', views.music_list, name='music_list'),
    path('music/upload/', views.upload_music, name='upload_music'),
    path('music/<int:music_id>/delete/', views.delete_music, name='delete_music'),
    path('sfx/', views.sfx_list, name='sfx_list'),
    path('sfx/upload/', views.upload_sfx, name='upload_sfx'),
    path('sfx/<int:sfx_id>/delete/', views.delete_sfx, name='delete_sfx'),
    
    # Feature: Visual Script Editor
    path('script/new/', views.create_script_draft, name='create_script_draft'),
    path('project/<int:project_id>/editor/', views.project_editor, name='project_editor'),
    path('api/project/<int:project_id>/script/', views.get_project_script_json, name='get_project_script_json'),
    path('api/project/<int:project_id>/script/save/', views.save_project_script_json, name='save_project_script_json'),
    # HTMX endpoints for modal
    path('api/project/<int:project_id>/scene/form/', views.scene_form, name='scene_form'),
]
