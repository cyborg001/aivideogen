import requests
from bs4 import BeautifulSoup

url = "https://rss.com/blog"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    print(f"Inspeccionando: {url}")
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Tipo de contenido: {response.headers.get('Content-Type')}")
    
    if 'xml' in response.headers.get('Content-Type', '').lower():
        print("¡Es un feed XML válido!")
    else:
        print("NO es un feed XML/RSS. Es una página web.")
        soup = BeautifulSoup(response.content, 'html.parser')
        rss_links = soup.find_all('link', type='application/rss+xml')
        if rss_links:
            print(f"Feed encontrado en la página: {rss_links[0].get('href')}")
        else:
            print("No se encontraron enlaces RSS explícitos en el header.")
            # Heuristic check
            print(f"Prueba con /feed: {url}/feed")
            
except Exception as e:
    print(f"Error: {e}")
