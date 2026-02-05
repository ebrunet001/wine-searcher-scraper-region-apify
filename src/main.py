"""
Wine-Searcher Region Scraper

Scrapes wine data from Wine-Searcher regions using SuperScraper API.
Extracts: Product name, Grape variety, Popularity, Critics' score, Average price.
Supports recursive sub-region scraping (Top 25 wines per region).
"""

import os
import re
import asyncio
from urllib.parse import urljoin, urlparse
from typing import Optional
from dataclasses import dataclass, asdict

import httpx
from bs4 import BeautifulSoup
from apify import Actor


@dataclass
class WineData:
    """Data structure for a wine entry."""
    product_name: str
    product_url: str
    grape: str
    grape_url: Optional[str]
    popularity: str
    critics_score: str
    avg_price: str
    region: str
    source_url: str


class WineSearcherScraper:
    """Scraper for Wine-Searcher region pages using SuperScraper API."""

    BASE_URL = "https://www.wine-searcher.com"
    SUPERSCRAPER_URL = "https://super-scraper-api.apify.actor/"

    def __init__(
        self,
        start_url: str,
        scrape_sub_regions: bool = True,
        max_depth: int = 10,
        tab_filter: str = "mostpopular",
        request_timeout: int = 120,
    ):
        self.start_url = start_url
        self.scrape_sub_regions = scrape_sub_regions
        self.max_depth = max_depth
        self.tab_filter = tab_filter
        self.request_timeout = request_timeout

        self.visited_regions: set[str] = set()
        self.seen_wine_urls: set[str] = set()
        self.wines_scraped = 0
        self.regions_scraped = 0

        # Get Apify token
        self.apify_token = os.environ.get('APIFY_TOKEN')
        if not self.apify_token:
            raise ValueError("APIFY_TOKEN environment variable is required")

    def _extract_region_name(self, url: str) -> str:
        """Extract region name from URL."""
        path = urlparse(url).path
        match = re.search(r'/regions-(.+?)(?:\?|$)', path)
        if match:
            region_name = match.group(1)
            region_name = region_name.replace('+', ' ').replace('%20', ' ')
            return region_name.title()
        return "Unknown"

    def _parse_wine_table(self, html: str, source_url: str) -> list[WineData]:
        """Parse the wine table from HTML content."""
        wines = []
        soup = BeautifulSoup(html, 'lxml')
        region_name = self._extract_region_name(source_url)

        # Find wine links - they link to /find/ pages
        for link in soup.find_all('a', href=lambda h: h and '/find/' in h):
            try:
                product_name = link.get_text(strip=True)
                if not product_name or len(product_name) < 10:
                    continue

                product_url = urljoin(self.BASE_URL, link.get('href', ''))

                # Skip duplicates
                if product_url in self.seen_wine_urls:
                    continue
                self.seen_wine_urls.add(product_url)

                # Find parent row/container to extract other data
                parent = link.find_parent('tr') or link.find_parent('div')
                if not parent:
                    continue

                parent_text = parent.get_text()
                parent_html = str(parent)

                # Extract grape
                grape = ""
                grape_url = None
                grape_link = parent.find('a', href=lambda h: h and '/grape-' in h)
                if grape_link:
                    grape = grape_link.get_text(strip=True)
                    grape_url = urljoin(self.BASE_URL, grape_link.get('href', ''))

                # Extract popularity
                popularity = ""
                pop_match = re.search(r'(\d+)(?:st|nd|rd|th)\s+in\s+popularity', parent_text, re.IGNORECASE)
                if pop_match:
                    rank = pop_match.group(1)
                    rank_int = int(rank)
                    suffix = 'th'
                    if rank_int % 100 not in [11, 12, 13]:
                        if rank_int % 10 == 1:
                            suffix = 'st'
                        elif rank_int % 10 == 2:
                            suffix = 'nd'
                        elif rank_int % 10 == 3:
                            suffix = 'rd'
                    popularity = f"{rank}{suffix} in popularity"

                # Extract price - try multiple patterns
                avg_price = ""
                # Pattern 1: Currency symbol followed by number (with possible whitespace/newlines)
                price_match = re.search(r'[\$€£][\s\n]*[\d,]+(?:\.\d{2})?', parent_text)
                if price_match:
                    # Clean up the match - remove newlines and extra spaces
                    price_raw = price_match.group(0)
                    avg_price = re.sub(r'\s+', ' ', price_raw).strip()

                # Pattern 2: Look for "X,XXX / 750ml" pattern if no currency found
                if not avg_price:
                    price_match2 = re.search(r'([\d,]+(?:\.\d{2})?)\s*/\s*750ml', parent_text)
                    if price_match2:
                        avg_price = f"${price_match2.group(1)}"

                # Pattern 3: Look for price in specific div class
                if not avg_price:
                    price_elem = parent.find(string=re.compile(r'[\$€£]'))
                    if price_elem:
                        # Get the next sibling or parent text for the number
                        price_container = price_elem.find_parent()
                        if price_container:
                            container_text = price_container.get_text()
                            price_match3 = re.search(r'[\$€£][\s\n]*[\d,]+', container_text)
                            if price_match3:
                                avg_price = re.sub(r'\s+', ' ', price_match3.group(0)).strip()

                # Extract critics score
                critics_score = ""
                score_match = re.search(r'(\d{2})\s*/\s*100', parent_text)
                if score_match:
                    critics_score = f"{score_match.group(1)} / 100"

                wine = WineData(
                    product_name=product_name,
                    product_url=product_url,
                    grape=grape,
                    grape_url=grape_url,
                    popularity=popularity,
                    critics_score=critics_score,
                    avg_price=avg_price,
                    region=region_name,
                    source_url=source_url
                )
                wines.append(wine)

            except Exception as e:
                Actor.log.debug(f"Error parsing wine: {e}")
                continue

        return wines

    def _extract_sub_regions(self, html: str, current_url: str) -> list[str]:
        """Extract sub-region URLs from the page, filtering out major non-related regions."""
        sub_regions = []
        soup = BeautifulSoup(html, 'lxml')

        # Major world/country/top-level regions to exclude (navigation links)
        EXCLUDED_REGIONS = {
            # Countries
            'france', 'italy', 'spain', 'portugal', 'germany', 'austria',
            'usa', 'australia', 'chile', 'argentina', 'new+zealand', 'south+africa',
            'greece', 'hungary', 'england', 'canada', 'mexico', 'brazil',
            # Major French regions (not sub-regions of Burgundy)
            'loire', 'rhone', 'bordeaux', 'champagne', 'alsace', 'provence',
            'languedoc', 'roussillon', 'southwest+france', 'jura', 'savoie',
            'corsica', 'beaujolais',
            # Major Italian regions
            'tuscany', 'piedmont', 'veneto', 'sicily', 'lombardy',
            # Major Spanish regions
            'rioja', 'ribera+del+duero', 'priorat', 'catalonia',
            # Other major regions
            'california', 'oregon', 'washington', 'napa+valley', 'sonoma',
            'barossa', 'marlborough', 'stellenbosch', 'mendoza',
        }

        region_links = soup.find_all('a', href=re.compile(r'^/regions-[a-zA-Z0-9%+\-]+$'))

        for link in region_links:
            href = link.get('href', '')
            full_url = urljoin(self.BASE_URL, href)
            link_region = href.replace('/regions-', '').lower()

            # Skip if already visited or is the root regions page
            if full_url in self.visited_regions:
                continue
            if href == '/regions':
                continue

            # Skip excluded major regions
            if link_region in EXCLUDED_REGIONS:
                continue

            sub_regions.append(full_url)

        return list(set(sub_regions))

    async def _fetch_with_superscraper(self, url: str, client: httpx.AsyncClient) -> Optional[str]:
        """Fetch URL using SuperScraper API."""
        params = {
            'url': url,
            'render_js': 'true',
            'premium_proxy': 'true',
            'wait_for': 'table',
            'wait': '3000',
            'json_response': 'true',
            'timeout': str(self.request_timeout * 1000),
        }

        headers = {
            'Authorization': f'Bearer {self.apify_token}',
            'Accept': 'application/json',
        }

        try:
            Actor.log.debug(f"Fetching: {url}")
            response = await client.get(
                self.SUPERSCRAPER_URL,
                params=params,
                headers=headers,
                timeout=self.request_timeout + 30,
            )

            if response.status_code != 200:
                Actor.log.warning(f"SuperScraper returned status {response.status_code}")
                return None

            result = response.json()
            body = result.get('body') or result.get('html') or result.get('content') or ''

            if not body:
                Actor.log.warning("Empty response from SuperScraper")
                return None

            # Check for block indicators
            lower_body = body.lower()
            if 'access denied' in lower_body or 'captcha' in lower_body:
                Actor.log.warning("Block detected in page content")
                return None

            Actor.log.debug(f"Successfully fetched {len(body)} bytes")
            return body

        except Exception as e:
            Actor.log.error(f"SuperScraper error: {e}")
            return None

    async def _fetch_with_retry(self, url: str, client: httpx.AsyncClient) -> Optional[str]:
        """Fetch URL with retry logic."""
        for attempt in range(3):
            html = await self._fetch_with_superscraper(url, client)
            if html:
                return html
            if attempt < 2:
                Actor.log.warning(f"Attempt {attempt + 1} failed, retrying...")
                await asyncio.sleep(5 * (attempt + 1))
        return None

    async def _scrape_region(self, base_url: str, client: httpx.AsyncClient) -> tuple[list[WineData], list[str]]:
        """Scrape a single region page."""
        url = f"{base_url}?tab_F={self.tab_filter}"

        html = await self._fetch_with_retry(url, client)
        if not html:
            Actor.log.warning(f"Failed to fetch region")
            return [], []

        wines = self._parse_wine_table(html, url)
        sub_regions = self._extract_sub_regions(html, url)

        return wines, sub_regions

    async def run(self) -> int:
        """Run the scraper using SuperScraper API."""
        Actor.log.info("Starting Wine-Searcher scraper (SuperScraper API)")
        Actor.log.info(f"  Start URL: {self.start_url}")
        Actor.log.info(f"  Scrape sub-regions: {self.scrape_sub_regions}")
        Actor.log.info(f"  Max depth: {self.max_depth}")
        Actor.log.info(f"  Tab filter: {self.tab_filter}")

        async with httpx.AsyncClient() as client:
            # Queue of regions to scrape: (url, depth)
            queue: list[tuple[str, int]] = [(self.start_url, 0)]

            while queue:
                url, depth = queue.pop(0)
                base_url = url.split('?')[0]

                if base_url in self.visited_regions:
                    continue

                self.visited_regions.add(base_url)

                region_name = self._extract_region_name(url)
                Actor.log.info(f"Scraping region: {region_name} (depth: {depth})")

                wines, sub_regions = await self._scrape_region(base_url, client)

                Actor.log.info(f"  Found {len(wines)} new wines")

                if wines:
                    wine_dicts = [asdict(w) for w in wines]
                    await Actor.push_data(wine_dicts)
                    self.wines_scraped += len(wines)

                self.regions_scraped += 1

                # Add sub-regions to queue
                if self.scrape_sub_regions and depth < self.max_depth:
                    new_sub_regions = [s for s in sub_regions if s.split('?')[0] not in self.visited_regions]
                    Actor.log.info(f"  Found {len(new_sub_regions)} new sub-regions")
                    for sub_url in new_sub_regions:
                        queue.append((sub_url, depth + 1))

                # Delay between regions
                await asyncio.sleep(2)

        Actor.log.info("=" * 50)
        Actor.log.info("SCRAPING COMPLETE")
        Actor.log.info("=" * 50)
        Actor.log.info(f"  Regions scraped: {self.regions_scraped}")
        Actor.log.info(f"  Total unique wines: {self.wines_scraped}")

        return self.wines_scraped


async def main():
    """Main entry point for the Actor."""
    async with Actor:
        actor_input = await Actor.get_input() or {}

        start_url = actor_input.get('startUrl', 'https://www.wine-searcher.com/regions-burgundy')
        scrape_sub_regions = actor_input.get('scrapeSubRegions', True)
        max_depth = actor_input.get('maxDepth', 10)
        tab_filter = actor_input.get('tabFilter', 'mostpopular')
        request_timeout = actor_input.get('requestTimeout', 120)

        if not start_url.startswith('https://www.wine-searcher.com/regions-'):
            Actor.log.error(f"Invalid start URL: {start_url}")
            Actor.log.error("URL must be a Wine-Searcher region page")
            await Actor.exit(exit_code=1)
            return

        scraper = WineSearcherScraper(
            start_url=start_url,
            scrape_sub_regions=scrape_sub_regions,
            max_depth=max_depth,
            tab_filter=tab_filter,
            request_timeout=request_timeout,
        )

        total_wines = await scraper.run()

        await Actor.set_value('OUTPUT', {
            'totalWines': total_wines,
            'regionsScraped': scraper.regions_scraped,
            'startUrl': start_url
        })
