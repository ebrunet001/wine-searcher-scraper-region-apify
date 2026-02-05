"""
Entry point for the Wine-Searcher scraper Actor.
"""
import asyncio
import logging

from apify.log import ActorLogFormatter

from .main import main

# Configure logging
handler = logging.StreamHandler()
handler.setFormatter(ActorLogFormatter())

apify_logger = logging.getLogger('apify')
apify_logger.setLevel(logging.INFO)
apify_logger.addHandler(handler)

# Run the Actor
asyncio.run(main())
