# Wine Searcher Scraper Region - Search Rank + Rating + Avg Price

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue)](https://apify.com/scrapmania/wine-searcher-scraper-region---search-rank-rating-avg-price)

Scrape wine data from [Wine-Searcher](https://www.wine-searcher.com) region pages. This Actor extracts detailed wine information including product names, grape varieties, popularity rankings, critics' scores, and average prices.

## Apify Store

- **Actor URL**: https://apify.com/scrapmania/wine-searcher-scraper-region---search-rank-rating-avg-price
- **Console URL**: https://console.apify.com/actors/cLCvbvUnes441I1SY

## Features

- **Recursive Sub-Region Scraping**: Start from a country or region and automatically discover and scrape all sub-regions
- **Pagination Support**: Scrape multiple pages per region (up to 500 wines per region)
- **Multiple Sorting Options**: Choose between Most Popular, Best Rated, Best Value, Most Expensive, or Cheapest wines
- **Configurable Depth**: Control how deep the scraper goes into sub-regions
- **Proxy Support**: Built-in Apify proxy integration for avoiding rate limits

## Input

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `startUrl` | string | Wine-Searcher region URL to start from | Required |
| `scrapeSubRegions` | boolean | Recursively scrape sub-regions | `true` |
| `maxDepth` | integer | Maximum depth for sub-region crawling | `10` |
| `maxPagesPerRegion` | integer | Max pagination pages per region (25 wines/page) | `20` |
| `tabFilter` | string | Wine sorting: mostpopular, best, bestvalue, mostexpensive, cheapest | `mostpopular` |
| `proxyConfiguration` | object | Proxy settings | Apify Proxy |
| `maxConcurrency` | integer | Concurrent requests | `5` |
| `requestTimeout` | integer | Request timeout in seconds | `60` |

### Example Input

```json
{
    "startUrl": "https://www.wine-searcher.com/regions-italy",
    "scrapeSubRegions": true,
    "maxDepth": 5,
    "maxPagesPerRegion": 10,
    "tabFilter": "mostpopular"
}
```

## Output

Each wine is saved with the following fields:

| Field | Description | Example |
|-------|-------------|---------|
| `product_name` | Full wine name | "Domaine de la Romanee-Conti Romanee-Conti Grand Cru" |
| `product_url` | Link to wine page | "https://www.wine-searcher.com/find/..." |
| `grape` | Grape variety | "Pinot Noir" |
| `grape_url` | Link to grape page | "https://www.wine-searcher.com/grape-384-pinot-noir" |
| `popularity` | Popularity ranking | "12th in popularity" |
| `critics_score` | Average critics score | "98 / 100" |
| `avg_price` | Average price per 750ml | "$ 24,099" |
| `region` | Region name | "Burgundy" |
| `source_url` | URL scraped | "https://www.wine-searcher.com/regions-burgundy" |

### Example Output

```json
{
    "product_name": "Tenuta San Guido Sassicaia Bolgheri, Tuscany, Italy",
    "product_url": "https://www.wine-searcher.com/find/tenute+st+guido+sassicaia+bolgheri+tuscany+italy",
    "grape": "Cabernet Franc - Cabernet Sauvignon",
    "grape_url": "https://www.wine-searcher.com/grape-1828-cabernet-franc-cabernet-sauvignon",
    "popularity": "8th in popularity",
    "critics_score": "96 / 100",
    "avg_price": "$ 395",
    "region": "Italy",
    "source_url": "https://www.wine-searcher.com/regions-italy?tab_F=mostpopular"
}
```

## Usage Examples

### Scrape all wines from Italy

```json
{
    "startUrl": "https://www.wine-searcher.com/regions-italy",
    "scrapeSubRegions": true,
    "maxDepth": 10
}
```

### Scrape only Burgundy (no sub-regions)

```json
{
    "startUrl": "https://www.wine-searcher.com/regions-burgundy",
    "scrapeSubRegions": false
}
```

### Find the best value wines in France

```json
{
    "startUrl": "https://www.wine-searcher.com/regions-france",
    "scrapeSubRegions": true,
    "tabFilter": "bestvalue"
}
```

## Region URL Examples

- **Countries**:
  - Italy: `https://www.wine-searcher.com/regions-italy`
  - France: `https://www.wine-searcher.com/regions-france`
  - USA: `https://www.wine-searcher.com/regions-usa`

- **Regions**:
  - Burgundy: `https://www.wine-searcher.com/regions-burgundy`
  - Tuscany: `https://www.wine-searcher.com/regions-tuscany`
  - Napa Valley: `https://www.wine-searcher.com/regions-napa+valley`

- **Sub-Regions**:
  - Barolo: `https://www.wine-searcher.com/regions-barolo`
  - Chablis: `https://www.wine-searcher.com/regions-chablis`
  - Chianti Classico: `https://www.wine-searcher.com/regions-chianti+classico`

## Important: Rate Limiting & Proxy Configuration

Wine-Searcher has aggressive anti-scraping measures. **Proxy support is essential** for production use.

### Recommended Proxy Configuration

When running on Apify, use residential or datacenter proxies:

```json
{
    "startUrl": "https://www.wine-searcher.com/regions-italy",
    "scrapeSubRegions": true,
    "proxyConfiguration": {
        "useApifyProxy": true,
        "apifyProxyGroups": ["RESIDENTIAL"]
    },
    "maxConcurrency": 1
}
```

### Rate Limiting Behavior

- The scraper includes random delays (3-8 seconds) between requests
- On 403/429 responses, it enters a global cooldown (30-120+ seconds)
- **Local testing without proxy will likely result in IP blocking**
- When deploying on Apify, always enable proxy configuration

## Tips

1. **Use Proxies**: Enable Apify Proxy for all scrapes to avoid rate limiting
2. **Low Concurrency**: Keep `maxConcurrency` at 1 for this site
3. **Start Small**: Test with `scrapeSubRegions: false` and `maxPagesPerRegion: 2` first
4. **Monitor Depth**: Countries like Italy have many sub-regions; limit `maxDepth` if needed

## Local Development

```bash
# Clone and install dependencies
cd wine-searcher-scraper
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run locally
python -m src
```

## License

MIT
