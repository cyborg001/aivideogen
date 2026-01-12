from django.test import TestCase
from django.urls import reverse
from .models import NewsSource, NewsItem
import datetime

class ResearcherTests(TestCase):
    def setUp(self):
        self.source = NewsSource.objects.create(
            name="Test Source",
            url="https://test.com",
            category="ai"
        )
        self.item = NewsItem.objects.create(
            title="Test News",
            summary="Test Summary",
            url="https://test.com/news1",
            source=self.source,
            category="ai",
            published_at=datetime.datetime.now()
        )

    def test_news_list_view(self):
        response = self.client.get(reverse('researcher:news_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test News")

    def test_news_search(self):
        response = self.client.get(reverse('researcher:news_list') + '?q=Test')
        self.assertContains(response, "Test News")
        
        response = self.client.get(reverse('researcher:news_list') + '?q=Nonexistent')
        self.assertNotContains(response, "Test News")

    def test_news_refresh_view(self):
        # Refresh is a POST view
        response = self.client.post(reverse('researcher:news_refresh'))
        self.assertEqual(response.status_code, 302) # Redirects back
