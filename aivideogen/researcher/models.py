from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

class NewsSource(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    category_old = models.CharField(max_length=50, blank=True, null=True)
    is_secure = models.BooleanField(default=True)
    is_rss = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category.name if self.category else 'Sin categoría'})"

class NewsItem(models.Model):
    title = models.CharField(max_length=500)
    summary = models.TextField()
    url = models.URLField(unique=True)
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    category_old = models.CharField(max_length=50, blank=True, null=True)
    impact_score = models.IntegerField(default=5)  # 1-10
    published_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title
