from django.urls import path
from . import views

app_name = 'researcher'

urlpatterns = [
    path('', views.NewsListView.as_view(), name='news_list_root'),
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/refresh/', views.NewsRefreshView.as_view(), name='news_refresh'),
    
    path('sources/', views.SourceListView.as_view(), name='source_list'),
    path('sources/add/', views.NewsSourceCreateView.as_view(), name='source_add'),
    path('sources/<int:pk>/delete/', views.NewsSourceDeleteView.as_view(), name='source_delete'),
    
    # Categorías ahora son auto-gestionadas (se crean/eliminan automáticamente)
    # path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    # path('categories/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
]
