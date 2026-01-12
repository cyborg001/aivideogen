import requests
import xml.etree.ElementTree as ET
from .models import NewsSource, NewsItem, Category
from django.utils import timezone
from datetime import datetime
import re
import urllib.parse
from django.db import models

from django.conf import settings
from django.db import IntegrityError

def translate_text(text, langpair="en|es"):
    """
    Translates text using the free MyMemory API.
    Supports an optional email key from settings to increase limits.
    """
    if not text or len(text.strip()) == 0:
        return text
    
    try:
        text_to_translate = text[:900]
        email = getattr(settings, 'MYMEMORY_EMAIL', None)
        params = {
            'q': text_to_translate,
            'langpair': langpair,
        }
        if email:
            params['de'] = email
            
        url = "https://api.mymemory.translated.net/get?" + urllib.parse.urlencode(params)
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            translated = data.get("responseData", {}).get("translatedText")
            if translated:
                return translated
    except Exception as e:
        print(f"Translation error: {e}")
    
    return text # Fallback to original

def parse_rss(source):
    """
    Parses an RSS or Atom feed and returns a list of NewsItem data.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5'
        }
        response = requests.get(source.url, timeout=15, headers=headers)
        if response.status_code != 200:
            print(f"DEBUG: {source.name} resulto en error HTTP {response.status_code}")
            return []
        
        content = response.content.strip()
        if not content:
            return []

        # Remove BOM if present
        if content.startswith(b'\xef\xbb\xbf'):
            content = content[3:]

        root = ET.fromstring(content)
        items = []
        
        # Detection: RSS vs Atom
        is_atom = 'feed' in root.tag.lower()
        
        if is_atom:
            ns = {'ns': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('ns:entry', ns):
                title = entry.find('ns:title', ns).text if entry.find('ns:title', ns) is not None else "Sin Título"
                link = ""
                link_tag = entry.find('ns:link', ns)
                if link_tag is not None:
                    link = link_tag.get('href', '')
                
                summary = ""
                summary_tag = entry.find('ns:summary', ns) or entry.find('ns:content', ns)
                if summary_tag is not None:
                    summary = summary_tag.text if summary_tag.text else ""
                
                pub_date_str = entry.find('ns:updated', ns).text if entry.find('ns:updated', ns) is not None else None
                summary = re.sub('<[^<]+?>', '', summary)[:500]
                
                # Robust Date Parsing
                pub_date = timezone.now()
                if pub_date_str:
                    try:
                        pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                        if not timezone.is_aware(pub_date):
                            pub_date = timezone.make_aware(pub_date)
                    except: pass

                items.append({
                    'title': title, 'summary': summary, 'url': link,
                    'source': source, 'category': source.category,
                    'impact_score': 7, 'published_at': pub_date
                })
        else:
            # RSS 2.0 - More robust matching for Diario Libre and others
            # Some feeds put items directly under root, others under channel
            found_items = root.findall('.//item')
            for item in found_items:
                title = item.find('title').text if item.find('title') is not None else "Sin Título"
                
                # Link can be in <link> or <guid isPermaLink="true">
                link = item.find('link').text if item.find('link') is not None else ""
                if not link:
                    guid = item.find('guid')
                    if guid is not None and guid.get('isPermaLink', 'true') == 'true':
                        link = guid.text
                
                desc = ""
                desc_tag = item.find('description')
                if desc_tag is not None:
                    desc = desc_tag.text if desc_tag.text else ""
                
                pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else None
                desc = re.sub('<[^<]+?>', '', desc)[:500]
                
                # Robust Date Parsing for RSS
                pub_date = timezone.now()
                if pub_date_str:
                    date_formats = [
                        '%a, %d %b %Y %H:%M:%S',
                        '%a, %d %b %Y %H:%M:%S %z',
                        '%Y-%m-%dT%H:%M:%S%z',
                        '%d %b %Y %H:%M:%S %Z'
                    ]
                    for fmt in date_formats:
                        try:
                            clean_date = pub_date_str.split(',')[1].strip() if ',' in pub_date_str else pub_date_str
                            # Try with timezone if possible
                            pub_date = datetime.strptime(pub_date_str[:25].strip(), '%a, %d %b %Y %H:%M:%S')
                            pub_date = timezone.make_aware(pub_date)
                            break
                        except:
                            try:
                                # Fallback to standard ISO if previous fails
                                pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                                break
                            except: continue

                items.append({
                    'title': title, 'summary': desc, 'url': link,
                    'source': source, 'category': source.category,
                    'impact_score': 7, 'published_at': pub_date
                })
        
        print(f"DEBUG: Fuente {source.name} procesada: {len(items)} noticias encontradas.")
        return items
    except Exception as e:
        print(f"DEBUG: Error critico en {source.name}: {e}")
        return []

def fetch_latest_ai_news():
    """
    Fetches latest news. If sources are RSS, it parses them. 
    Includes Spanish native sources and translates English content.
    """
    # 1. Ensure default sources exist (Spanish & English)
    sources_to_ensure = [
        {
            'url': "https://rss.arxiv.org/rss/cs.AI",
            'name': 'Arxiv AI (Investigación)',
            'category': 'discovery',
            'is_secure': True,
            'is_rss': True
        },
        {
            'url': "https://feeds.weblogssl.com/xataka2",
            'name': 'Xataka (Tecnología)',
            'category': 'tech',
            'is_secure': True,
            'is_rss': True
        },
        {
            'url': "https://feeds.weblogssl.com/genbeta",
            'name': 'Genbeta (Software/IA)',
            'category': 'ai',
            'is_secure': True,
            'is_rss': True
        }
    ]

    for src_data in sources_to_ensure:
        # Create or update to ensure is_rss is True and category is correct
        cat, _ = Category.objects.get_or_create(slug=src_data['category'], defaults={'name': src_data['category'].capitalize()})
        NewsSource.objects.update_or_create(
            url=src_data['url'],
            defaults={
                'name': src_data['name'],
                'category': cat,
                'is_secure': src_data['is_secure'],
                'is_rss': src_data['is_rss']
            }
        )
    
    # 2. Add some curated hardcoded data in Spanish if empty
    if NewsItem.objects.count() == 0:
        cat_ai, _ = Category.objects.get_or_create(slug='ai', defaults={'name': 'IA'})
        openai_src, _ = NewsSource.objects.get_or_create(
            url="https://openai.com/blog", 
            defaults={'name': "OpenAI Blog", 'category': cat_ai, 'is_secure': True}
        )
        NewsItem.objects.get_or_create(
            url='https://openai.com/blog/gpt-5-2-and-codex',
            defaults={
                'title': 'GPT-5.2 y Codex: Razonamiento Avanzado para Agentes Autónomos',
                'summary': 'La última versión de OpenAI se centra en la ingeniería de software compleja y la investigación en ciberseguridad.',
                'source': openai_src,
                'category': cat_ai,
                'impact_score': 9,
                'published_at': timezone.now()
            }
        )

    # 3. Dynamic Refresh: Fetch from all RSS sources
    rss_sources = NewsSource.objects.filter(is_rss=True)
    new_items_count = 0
    seen_urls = set()
    
    for source in rss_sources:
        print(f"Refrescando fuente RSS: {source.name}")
        items = parse_rss(source)
        
        # Limit to top 20 items to prevent server freeze due to massive translations
        total_items = len(items)
        items = items[:20]
        if total_items > 20:
            print(f"DEBUG: Limitando a las top 20 noticias de {total_items} encontradas para evitar bloqueos.")

        for data in items:
            url = data.get('url')
            if not url or url in seen_urls:
                continue
                
            seen_urls.add(url)
            
            if not NewsItem.objects.filter(url=url).exists():
                # Translation for non-Spanish sources (Arxiv, etc)
                is_english = any(domain in source.url.lower() for domain in ["arxiv", "openai", "google", "mit.edu"])
                
                if is_english:
                    print(f"DEBUG: Traduciendo noticia: {data['title'][:50]}...")
                    data['title'] = translate_text(data['title'])
                    data['summary'] = translate_text(data['summary'])
                
                try:
                    NewsItem.objects.create(**data)
                    new_items_count += 1
                except IntegrityError:
                    continue
                except Exception as e:
                    print(f"Error creating NewsItem for {url}: {e}")

    return f"¡Refrescado! Se han encontrado {new_items_count} nuevas entradas."

