from config import celery_app
from scraper.scrape_threads import ThreadScraper


@celery_app.task
def thread_scraper_cron_task():
    """scrape threads every 2 minutes"""

    thread_scraper = ThreadScraper()
    thread_scraper.scrape_pages_and_save_threads()
