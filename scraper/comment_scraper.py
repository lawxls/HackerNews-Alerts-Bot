from time import sleep

from bs4 import BeautifulSoup
from dateutil import parser, tz
from django.conf import settings

from scraper.models import Comment
from scraper.types import ScrapedCommentData
from scraper.utils import start_request_session


class CommentScraper:
    """
    Scrape and (create or update) comments from Hacker News /newcomments page

    >>> from scraper.comment_scraper import CommentScraper
    >>> comment_scraper = CommentScraper()
    >>> comment_scraper.scrape()
    -> <list[Comment]>
    """

    def __init__(self, page_count: int = 10) -> None:
        self.page_count = page_count
        self.hn_request_session = start_request_session(domen=settings.HACKERNEWS_URL)

    def scrape(self) -> list[Comment]:
        scraped_comments = []

        last_comment_id = None
        for _ in range(self.page_count):
            sleep(0.5)

            url = f"{settings.HACKERNEWS_URL}newcomments"
            if last_comment_id:
                url += f"?next={last_comment_id}"

            response = self.hn_request_session.get(url)
            page = BeautifulSoup(response.text, "lxml")

            scraped_comments_by_page = self.parse_newcomments_page(bs4_page_data=page)
            last_comment_id = scraped_comments_by_page[-1]["comment_id"]

            scraped_comments.extend(scraped_comments_by_page)

        return self.create_or_update_comments(scraped_comments=scraped_comments)

    def parse_newcomments_page(self, bs4_page_data: BeautifulSoup) -> list[ScrapedCommentData]:
        scraped_comments = []

        rows = bs4_page_data.find_all("tr")
        for row in rows:
            if isinstance(row.get("class"), list) and row.get("class")[0] == "athing":

                created_at_str = row.find_all("span")[1].get("title")
                created_at = parser.parse(created_at_str).astimezone(tz.UTC)

                body = row.find_all("div")[2].find("span").text
                # add whitespaces before and after for full word matching
                body_with_whitespaces = f" {body} "

                scraped_comment = ScrapedCommentData(
                    comment_id=row.get("id"),
                    thread_id_int=row.find_all("span")[4].a.get("href").replace("item?id=", ""),
                    body=body_with_whitespaces,
                    username=row.find_all("a")[1].text,
                    comment_created_at=created_at,
                )
                scraped_comments.append(scraped_comment)

        return scraped_comments

    def create_or_update_comments(
        self, scraped_comments: list[ScrapedCommentData]
    ) -> list[Comment]:

        comments = []
        for scraped_comment in scraped_comments:
            comment, _ = Comment.objects.update_or_create(
                comment_id=scraped_comment["comment_id"], defaults=dict(scraped_comment)
            )
            comments.append(comment)

        return comments
