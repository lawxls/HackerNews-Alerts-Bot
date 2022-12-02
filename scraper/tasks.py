from config import celery_app
from scraper.comment_scraper import CommentScraper
from scraper.thread_scraper import ThreadScraper


@celery_app.task
def new_threads_scraper_cron_task() -> int:
    """scrape threads from /newest page"""

    newest_page_thread_scraper = ThreadScraper()
    threads = newest_page_thread_scraper.scrape()
    return len(threads)


@celery_app.task
def main_page_threads_scraper_cron_task() -> int:
    """scrape threads from /news page"""

    main_page_thread_scraper = ThreadScraper(page_to_scrape=ThreadScraper.NEWS, news_page_count=10)
    threads = main_page_thread_scraper.scrape()
    return len(threads)


@celery_app.task
def comments_scraper_cron_task() -> int:
    """scrape comments from /newcomments page"""

    comment_scraper = CommentScraper(page_count=5)
    comments = comment_scraper.scrape()
    return len(comments)
