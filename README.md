# Wine Searcher Scraper - Region Rankings, Ratings & Prices

Extract wine data from [Wine-Searcher](https://www.wine-searcher.com) region pages at scale. This Actor scrapes product names, grape varieties, popularity rankings, critics' scores, and average prices for every wine listed in a region. It supports recursive sub-region crawling, so you can start from a country like Italy and automatically discover and scrape all nested regions down to individual appellations.

## What does Wine Searcher Scraper do?

Wine-Searcher is the world's largest wine search engine, indexing over 18 million wines from 120,000+ merchants. This scraper extracts structured data from Wine-Searcher's **region pages**, which rank wines by popularity, ratings, value, or price within any geographic area.

For each wine found, the scraper extracts:
- **Product name** and direct link to the Wine-Searcher listing
- **Grape variety** (e.g., Pinot Noir, Chardonnay, Cabernet Sauvignon)
- **Popularity ranking** within the region
- **Critics' score** (average across professional reviewers, out of 100)
- **Average price** per 750ml bottle

The scraper handles pagination automatically (up to 500 wines per region) and can recursively crawl all sub-regions within a starting point.

## Why scrape Wine-Searcher?

Wine-Searcher region data is valuable for a wide range of professional and personal use cases:

- **Wine merchants and retailers**: Compare regional pricing, identify trending wines, and discover new products to stock
- **Sommeliers and buyers**: Build data-driven wine lists by analyzing ratings and popularity across appellations
- **Wine investors**: Track price movements and critics' scores for investment-grade wines by region
- **Market researchers**: Analyze competitive landscapes across wine regions and grape varieties
- **Data journalists**: Create visualizations and stories about wine trends, pricing, and regional comparisons
- **Wine collectors**: Discover highly-rated wines in specific regions before they become widely known
- **E-commerce platforms**: Enrich product catalogs with critics' scores and popularity data

## How to scrape Wine-Searcher by region

Follow these steps to extract wine data from any Wine-Searcher region:

1. **Find your region URL**: Go to [Wine-Searcher](https://www.wine-searcher.com) and navigate to a region page. The URL will look like `https://www.wine-searcher.com/regions-burgundy`.
2. **Set the start URL**: Paste the region URL into the `startUrl` field.
3. **Choose your sorting**: Select how wines should be sorted — Most Popular, Best Rated, Best Value, Most Expensive, or Cheapest.
4. **Configure depth**: Enable `Scrape Sub-Regions` to automatically discover and scrape nested regions. Set `Maximum Depth` to control how deep the crawl goes.
5. **Set pagination**: Choose how many pages per region to scrape (each page has ~25 wines).
6. **Run the Actor**: Click "Start" and wait for the results.
7. **Export your data**: Download the dataset in JSON, CSV, or Excel format.

## What data can you extract?

| Field | Description | Example |
|-------|-------------|---------|
| `product_name` | Full wine name with producer and region | "Domaine de la Romanee-Conti Romanee-Conti Grand Cru" |
| `product_url` | Direct link to the wine on Wine-Searcher | `https://www.wine-searcher.com/find/...` |
| `grape` | Grape variety or blend | "Pinot Noir" |
| `grape_url` | Link to the grape variety page | `https://www.wine-searcher.com/grape-384-pinot-noir` |
| `popularity` | Popularity ranking within the region | "12th in popularity" |
| `critics_score` | Average score from professional critics | "98 / 100" |
| `avg_price` | Average price per 750ml bottle | "$ 24,099" |
| `region` | Region name extracted from the page | "Burgundy" |
| `source_url` | The region page URL that was scraped | `https://www.wine-searcher.com/regions-burgundy` |

## Input configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `startUrl` | string | — | Wine-Searcher region URL (required) |
| `scrapeSubRegions` | boolean | `true` | Recursively scrape all sub-regions |
| `maxDepth` | integer | `10` | Maximum depth for sub-region crawling |
| `maxPagesPerRegion` | integer | `20` | Pages per region (25 wines/page, max 500 wines) |
| `tabFilter` | string | `mostpopular` | Sorting: mostpopular, best, bestvalue, mostexpensive, cheapest |
| `requestTimeout` | integer | `120` | HTTP request timeout in seconds |

### Example: Scrape Burgundy with sub-regions

```json
{
    "startUrl": "https://www.wine-searcher.com/regions-burgundy",
    "scrapeSubRegions": true,
    "maxDepth": 3,
    "maxPagesPerRegion": 5,
    "tabFilter": "mostpopular"
}
```

### Example: Best value wines in Italy (no sub-regions)

```json
{
    "startUrl": "https://www.wine-searcher.com/regions-italy",
    "scrapeSubRegions": false,
    "maxPagesPerRegion": 10,
    "tabFilter": "bestvalue"
}
```

### Example: Top-rated Champagnes

```json
{
    "startUrl": "https://www.wine-searcher.com/regions-champagne",
    "scrapeSubRegions": false,
    "tabFilter": "best"
}
```

## Output example

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

## How much does it cost?

The Actor uses pay-per-result pricing at **$0.005 per wine** extracted, plus standard Apify platform costs for compute time.

> **Important:** This Actor relies on [Apify SuperScraper](https://apify.com/apify/super-scraper) for JavaScript rendering and anti-bot bypass. SuperScraper is billed separately by Apify on each page fetch. **The cost shown in the Actor's Information tab does not include SuperScraper fees.** The total cost per run is the sum of this Actor's pay-per-result fee + compute time + SuperScraper usage.

| Scenario | Wines | Actor PPE cost | SuperScraper cost (approx.) | Total (approx.) |
|----------|-------|---------------|----------------------------|----------------|
| Single region, 1 page | ~25 | ~$0.13 | ~$0.05 | ~$0.18 |
| Single region, all pages | ~500 | ~$2.50 | ~$1.00 | ~$3.50 |
| Country with sub-regions (depth 2) | ~2,000 | ~$10 | ~$4.00 | ~$14 |
| Large country, full depth | ~10,000+ | ~$50+ | ~$20+ | ~$70+ |

Looking for a lower-cost alternative? Check out [Wine Searcher Region Rankings & Prices](https://apify.com/scrapmania/wine-searcher-region-rankings-prices), which uses built-in browser automation instead of SuperScraper — significantly reducing per-run costs.

## Region URL examples

| Region | URL |
|--------|-----|
| France | `https://www.wine-searcher.com/regions-france` |
| Italy | `https://www.wine-searcher.com/regions-italy` |
| USA | `https://www.wine-searcher.com/regions-usa` |
| Burgundy | `https://www.wine-searcher.com/regions-burgundy` |
| Bordeaux | `https://www.wine-searcher.com/regions-bordeaux` |
| Champagne | `https://www.wine-searcher.com/regions-champagne` |
| Tuscany | `https://www.wine-searcher.com/regions-tuscany` |
| Napa Valley | `https://www.wine-searcher.com/regions-napa+valley` |
| Barolo | `https://www.wine-searcher.com/regions-barolo` |
| Rioja | `https://www.wine-searcher.com/regions-rioja` |

## Tips for best results

1. **Start small**: Test with `scrapeSubRegions: false` and `maxPagesPerRegion: 1` to verify the output format before running large scrapes.
2. **Limit depth for large countries**: Countries like Italy or France have hundreds of sub-regions. Set `maxDepth` to 2-3 to keep run times manageable.
3. **Use sorting wisely**: "Most Popular" gives the most widely-known wines; "Best Rated" surfaces critic favorites; "Best Value" finds bargains.
4. **Monitor your runs**: Check the Actor logs to see which regions are being scraped and how many wines are extracted per region.
5. **Export and analyze**: Download results as CSV for spreadsheet analysis or JSON for programmatic processing.

## FAQ

**Q: How many wines can I extract per region?**
A: Each region page shows up to 25 wines per page. With `maxPagesPerRegion` set to 20 (default), you can extract up to 500 wines per region. Most regions have fewer wines than this limit.

**Q: Does the scraper handle anti-bot protection?**
A: Yes. The scraper uses Apify SuperScraper with JavaScript rendering and premium proxies to reliably access Wine-Searcher pages, which have aggressive anti-scraping measures.

**Q: What happens if a page fails to load?**
A: The scraper retries each page up to 3 times with increasing delays. If all retries fail, it skips the page and continues with the next one. Failed pages are logged as warnings.

**Q: Can I scrape a specific sub-region without scraping the parent?**
A: Yes. Set the `startUrl` directly to the sub-region URL (e.g., `https://www.wine-searcher.com/regions-barolo`) and disable `scrapeSubRegions` if you only want that specific area.

**Q: How long does a typical run take?**
A: A single region with 1 page takes about 10-15 seconds. A country with sub-regions and multiple pages can take 10-60 minutes depending on depth and pagination settings.

**Q: Are prices always in USD?**
A: Wine-Searcher displays prices based on the region page context. Most prices are shown in USD ($), but this depends on the page content. The scraper extracts the price exactly as displayed.

**Q: Can I schedule regular scrapes?**
A: Yes. Use Apify's built-in scheduler to run the Actor on a daily, weekly, or monthly basis. This is useful for tracking price trends and new wine releases.

**Q: What regions are supported?**
A: Any region page on Wine-Searcher is supported. This includes countries, wine regions, appellations, and sub-appellations. If the URL follows the pattern `https://www.wine-searcher.com/regions-{name}`, the scraper can handle it.

## Legal disclaimer

This Actor is provided for educational and research purposes. Users are responsible for complying with Wine-Searcher's terms of service and applicable laws. The scraper does not bypass any login or paywall — it only accesses publicly available pages.

## Support

- **Bug reports**: Open an issue on [GitHub](https://github.com/emmanuel-aristide/wine-searcher-scraper)
- **Questions**: Use the Actor's Issues tab on Apify
- **Feature requests**: Open a GitHub issue or contact the developer

## Related Actors

- [Vivino Wine Scraper](https://apify.com/scrapmania/vivino-powerful-scraper) — Extract wine ratings, prices, and reviews from Vivino
- [Vivino Search Results Scraper](https://apify.com/scrapmania/vivino-ratings-on-search-results) — Scrape Vivino search results with ratings
- [Millesima Wine Scraper](https://apify.com/scrapmania/millesima-wine-scraper) — Extract wine data from Millesima
