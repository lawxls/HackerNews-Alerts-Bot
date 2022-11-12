from config import celery_app
from scraper.service import ThreadScraper


@celery_app.task
def new_threads_scraper_cron_task():
    """scrape threads from /newest page"""

    newest_page_thread_scraper = ThreadScraper()
    newest_page_thread_scraper.scrape()


@celery_app.task
def main_page_threads_scraper_cron_task():
    """scrape threads from /news page"""

    main_page_thread_scraper = ThreadScraper(page_to_scrape=ThreadScraper.NEWS, news_page_count=10)
    main_page_thread_scraper.scrape()
