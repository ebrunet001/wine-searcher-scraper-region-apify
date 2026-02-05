import os
import httpx
from bs4 import BeautifulSoup
from apify import Actor

async def main():
    async with Actor:
        token = os.environ.get('APIFY_TOKEN')
        url = "https://super-scraper-api.apify.actor/"
        headers = {'Authorization': f'Bearer {token}'}
        
        async with httpx.AsyncClient() as client:
            # Test page 1
            Actor.log.info("Fetching page 1...")
            params1 = {
                'url': 'https://www.wine-searcher.com/regions-chablis?tab_F=mostpopular',
                'render_js': 'true',
                'premium_proxy': 'true',
                'wait': '5000',
                'wait_for': 'table',
                'json_response': 'true',
            }
            r1 = await client.get(url, params=params1, headers=headers, timeout=120)
            body1 = r1.json().get('body', '')
            
            soup1 = BeautifulSoup(body1, 'lxml')
            wines1 = []
            for link in soup1.find_all('a', href=lambda h: h and '/find/' in h):
                name = link.get_text(strip=True)
                if name and len(name) > 10:
                    wines1.append(name)
            
            Actor.log.info(f"Page 1: {len(wines1)} wines")
            for w in wines1[:5]:
                Actor.log.info(f"  - {w}")
            
            # Test page 2
            Actor.log.info("Fetching page 2...")
            params2 = {
                'url': 'https://www.wine-searcher.com/regions-chablis?Xlist_page=2&tab_F=mostpopular',
                'render_js': 'true',
                'premium_proxy': 'true', 
                'wait': '5000',
                'wait_for': 'table',
                'json_response': 'true',
            }
            r2 = await client.get(url, params=params2, headers=headers, timeout=120)
            body2 = r2.json().get('body', '')
            
            soup2 = BeautifulSoup(body2, 'lxml')
            wines2 = []
            for link in soup2.find_all('a', href=lambda h: h and '/find/' in h):
                name = link.get_text(strip=True)
                if name and len(name) > 10:
                    wines2.append(name)
            
            Actor.log.info(f"Page 2: {len(wines2)} wines")
            for w in wines2[:5]:
                Actor.log.info(f"  - {w}")
            
            # Compare
            if wines1 and wines2:
                Actor.log.info(f"Same first wine? {wines1[0] == wines2[0]}")
                Actor.log.info(f"Page 1 first: {wines1[0]}")
                Actor.log.info(f"Page 2 first: {wines2[0]}")

