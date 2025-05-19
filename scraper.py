import requests
from bs4 import BeautifulSoup
import re

def scrape_website(url, language):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return {'error': f'Failed to fetch {url}: {str(e)}'}

    soup = BeautifulSoup(response.text, 'html.parser')
    raw_text = ' '.join([elem.get_text() for elem in soup.find_all(['p', 'span', 'div'])])
    clean_text = re.sub(r'\s+', ' ', raw_text).strip()

    if language == 'en':
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if s.strip()]
    else:
        sentences = [s.strip() for s in clean_text.split('|') if s.strip()]

    return {'language': language, 'sentences': sentences}