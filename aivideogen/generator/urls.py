from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_project, name='create_project'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/start/', views.start_project, name='start_project'),
    path('project/<int:project_id>/stop/', views.stop_project, name='stop_project'),
    path('project/<int:project_id>/reset/', views.reset_project, name='reset_project'),
    path('project/<int:project_id>/clone/', views.clone_project, name='clone_project'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/upload/', views.upload_asset, name='upload_asset'),
    path('assets/<int:asset_id>/delete/', views.delete_asset, name='delete_asset'),
    path('api/browse/', views.browse_script, name='browse_script'),
    path('api/browse-folder/', views.browse_folder, name='browse_folder'),
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
    path('project/new/from_editor/', views.create_project_from_editor, name='create_project_from_editor'),
    path('project/<int:project_id>/editor/', views.project_editor, name='project_editor'),
    path('api/project/<int:project_id>/script/', views.get_project_script_json, name='get_project_script_json'),
    path('api/project/<int:project_id>/script/save/', views.save_project_script_json, name='save_project_script_json'),
    # HTMX endpoints for modal
    path('api/project/<int:project_id>/scene/form/', views.scene_form, name='scene_form'),
    
    # Independent Editor & Local File APIs
    path('script/editor/', views.script_editor_standalone, name='script_editor_standalone'),
    path('api/script/save_file/', views.save_script_file, name='save_script_file'),
    path('api/asset/browse/', views.browse_local_asset, name='browse_local_asset'),
    path('api/voice/upload/', views.upload_recording, name='upload_recording'),
    path('project/<int:project_id>/download_json/', views.download_project_script_json, name='download_project_script_json'),
    path('project/<int:project_id>/toggle_auto_upload/', views.toggle_auto_upload, name='toggle_auto_upload'),
    
    # Text/JSON Conversion APIs
    path('api/script/json_to_text/', views.json_to_text_api, name='api_json_to_text'),
    path('api/script/text_to_json/', views.text_to_json_api, name='api_text_to_json'),

    # Logs & System
    path('logs/', views.view_logs, name='view_logs'),
    path('api/heartbeat/', views.api_heartbeat, name='api_heartbeat'),
    
    # v12.5: Progress & Shutdown
    path('api/shutdown/', views.shutdown_app, name='shutdown_app'),
    path('api/project/<int:project_id>/status/', views.get_project_status, name='api_project_status'),

    # Carousel Tool (v15.9.2)
    path('tools/carousel/', views.carousel_tool_view, name='carousel_tool'),
    path('api/tools/process-carousel/', views.process_carousel_api, name='api_process_carousel'),
    path('api/tools/upload-carousel-images/', views.upload_carousel_images, name='api_upload_carousel_images'),
    path('api/tools/browse-images/', views.browse_images, name='api_browse_images'),
]

