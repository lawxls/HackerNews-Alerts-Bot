import pytest

from scraper.comment_scraper import CommentScraper


class TestCommentScraper:
    @pytest.mark.django_db
    def test_scraping_newcomments_page_success(self):
        """
        Test scraping news.ycombinator.com/newcomments page

        scraper should create/update 90 Comment objects
        """

        comment_scraper = CommentScraper(page_count=3)
        comments = comment_scraper.scrape()

        assert len(comments) == 90
