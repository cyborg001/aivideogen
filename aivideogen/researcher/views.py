from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, View, CreateView, DeleteView
from .models import NewsItem, NewsSource, Category
from .utils import fetch_latest_ai_news
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify

class NewsListView(ListView):
    model = NewsItem
    template_name = 'researcher/news_list.html'
    context_object_name = 'news_items'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        category_slug = self.request.GET.get('category')
        queryset = NewsItem.objects.all().order_by('-published_at')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(summary__icontains=query)
            )
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('name')
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context

class NewsRefreshView(View):
    def post(self, request):
        try:
            fetch_latest_ai_news()
            msg = "News hub updated with the latest breakthroughs!"
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': msg})
            messages.success(request, msg)
        except Exception as e:
            msg = f"Error refreshing news: {str(e)}"
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': msg})
            messages.error(request, msg)
        
        return redirect('researcher:news_list')

class SourceListView(ListView):
    model = NewsSource
    template_name = 'researcher/source_list.html'
    context_object_name = 'sources'

class NewsSourceCreateView(CreateView):
    model = NewsSource
    template_name = 'researcher/source_form.html'
    fields = ['name', 'url', 'category', 'is_secure', 'is_rss']
    success_url = reverse_lazy('researcher:source_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('name')
        return context

    def form_valid(self, form):
        # Auto-crear categoría desde el campo category_name si se proporciona
        category_name = self.request.POST.get('category_name', '').strip()
        if category_name:
            slug = slugify(category_name)
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': category_name.capitalize()}
            )
            form.instance.category = category
            if created:
                print(f"✓ Categoría '{category_name}' creada automáticamente")
        
        messages.success(self.request, "News source added successfully!")
        return super().form_valid(form)

class NewsSourceDeleteView(DeleteView):
    model = NewsSource
    success_url = reverse_lazy('researcher:source_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "News source deleted successfully.")
        return super().delete(request, *args, **kwargs)

class CategoryCreateView(View):
    def post(self, request):
        name = request.POST.get('name')
        if name:
            slug = slugify(name)
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name.capitalize()}
            )
            if created:
                return JsonResponse({'status': 'success', 'id': category.id, 'name': category.name})
            return JsonResponse({'status': 'error', 'message': 'La categoría ya existe'})
        return JsonResponse({'status': 'error', 'message': 'Nombre inválido'})

class CategoryDeleteView(View):
    def post(self, request):
        category_id = request.POST.get('category_id')
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            category.delete()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'ID inválido'})

