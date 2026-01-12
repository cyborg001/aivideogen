from django.contrib import admin
from .models import NewsSource, NewsItem, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_secure', 'added_at')
    list_filter = ('category', 'is_secure')
    search_fields = ('name', 'url')

@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'source', 'category', 'impact_score', 'published_at')
    list_filter = ('category', 'source', 'impact_score')
    search_fields = ('title', 'summary')
