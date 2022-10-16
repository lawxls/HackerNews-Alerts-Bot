import pytest

from scraper.service import ThreadScraper


class TestThreadScraper:
    @pytest.mark.django_db
    def test_scraping_main_page(self):
        """
        Test scraping news.ycombinator.com/news page.

        parser should create/update 30 Thread objects.
        there should be at least 1 Thread object where comments_count is not None.
        there should be at least 1 Thread object where score is not None.
        """

        thread_scraper = ThreadScraper()
        threads = thread_scraper.scrape_pages_and_save_threads(page_count=1)

        thread_with_score = next((thread for thread in threads if thread.score is not None), None)

        thread_with_comments_count = next(
            (thread for thread in threads if thread.comments_count is not None), None
        )

        assert thread_with_score is not None
        assert thread_with_comments_count is not None
        assert len(threads) == 30
