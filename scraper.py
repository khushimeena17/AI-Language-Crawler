import requests
from bs4 import BeautifulSoup
import re

def scrape_website(url, language):
    """
    Scrapes text from a website, cleans it, and returns structured sentences.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return {'error': f'Failed to fetch {url}: {str(e)}'}

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract all text from paragraphs, spans, divs
    raw_text = ' '.join([elem.get_text() for elem in soup.find_all(['p', 'span', 'div'])])

    # Clean and format text
    clean_text = re.sub(r'\s+', ' ', raw_text).strip()

    # Split into sentences (keeping sentence structure intact)
    sentences = re.split(r'(?<=[.!?])\s+', clean_text)

    return {'language': language, 'sentences': sentences}

