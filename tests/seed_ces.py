import os
import sys
import django

# Add the current directory to sys.path to find 'web_app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from researcher.models import NewsItem, NewsSource, Category

def seed_ces_news():
    source, _ = NewsSource.objects.get_or_create(
        url="https://www.ces.tech",
        defaults={'name': "Consumer Technology Association (CTA)"}
    )
    
    cat, _ = Category.objects.get_or_create(name="announcement")

    title = "CES 2026 Especial (10 Min): La Frontera de la IA Física"
    summary = (
        "Documental de 10 min. Innovaciones: LG CLOiD (7 DOF), Deep Robotics LYNX, "
        "Intel Panther Lake (180 TOPS) vs AMD Ryzen AI 400. Movilidad aérea: Joby y Archer/NVIDIA. "
        "Conectividad: Samsung/Keysight Direct-to-Cell. Accesibilidad: Naqi Neural Earbuds. "
        "Formato: 5 Columnas PRO."
    )
    
    from django.utils import timezone
    item, created = NewsItem.objects.get_or_create(
        url='https://www.ces.tech/announcements/2026',
        defaults={
            'title': title,
            'summary': summary,
            'source': source,
            'impact_score': 5,
            'category': cat,
            'published_at': timezone.now()
        }
    )
    
    if created:
        print(f"NewsItem creado: {title}")
    else:
        print(f"NewsItem ya existía: {title}")

if __name__ == "__main__":
    seed_ces_news()
