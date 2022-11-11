from config import celery_app
from scraper.service import ThreadScraper


@celery_app.task
def new_threads_scraper_cron_task():
    """scrape new threads every 2 minutes"""

    newest_page_thread_scraper = ThreadScraper()
    newest_page_thread_scraper.scrape()
