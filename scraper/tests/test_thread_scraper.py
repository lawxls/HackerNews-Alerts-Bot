import pytest

from scraper.thread_scraper import ThreadScraper


class TestThreadScraper:
    @pytest.mark.django_db
    def test_scraping_main_page_success(self):
        """
        Test scraping news.ycombinator.com/news page

        scraper should create/update 30 Thread objects
        there should be at least 1 Thread object where comments_count is not None
        there should be at least 1 Thread object where score is not None
        """

        main_page_thread_scraper = ThreadScraper(page_to_scrape=ThreadScraper.NEWS)
        threads = main_page_thread_scraper.scrape()

        thread_with_score = next((thread for thread in threads if thread.score is not None), None)

        thread_with_comments_count = next(
            (thread for thread in threads if thread.comments_count is not None), None
        )

        assert thread_with_score is not None
        assert thread_with_comments_count is not None
        assert len(threads) == 30

    @pytest.mark.django_db
    def test_scraping_newest_page_success(self):
        """
        Test scraping news.ycombinator.com/newest page
        """

        newest_page_thread_scraper = ThreadScraper()
        threads = newest_page_thread_scraper.scrape()

        thread_with_score = next((thread for thread in threads if thread.score is not None), None)

        thread_with_comments_count = next(
            (thread for thread in threads if thread.comments_count is not None), None
        )

        assert thread_with_score is not None
        assert thread_with_comments_count is not None
        assert len(threads) == 30
