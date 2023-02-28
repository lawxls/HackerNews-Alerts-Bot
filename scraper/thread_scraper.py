from time import sleep

from bs4 import BeautifulSoup
from dateutil import parser, tz
from django.conf import settings
from django.utils import timezone

from scraper.models import Thread
from scraper.types import ScrapedThreadData, ThreadMetaData
from scraper.utils import start_request_session


class ThreadScraper:
    """
    Scrape and (create or update) threads from Hacker News /newest or /news pages

    Scrape /newest page
    >>> from scraper.parsers import ThreadScraper
    >>> newest_threads_scraper = ThreadScraper()
    >>> newest_threads_scraper.scrape()
    -> <list[Thread]>

    Scrape threads from first 10 /news pages
    >>> from scraper.parsers import ThreadScraper
    >>> news_page_threads_scraper = ThreadScraper(
            page_to_scrape=ThreadScraper.NEWS, news_page_count=10
        )
    >>> news_page_threads_scraper.scrape()
    -> <list[Thread]>
    """

    NEWS = "NEWS"
    NEWEST = "NEWEST"

    def __init__(self, page_to_scrape: str = NEWEST, news_page_count: int = 0) -> None:
        self.page_to_scrape = page_to_scrape
        self.hn_request_session = start_request_session(domen=settings.HACKERNEWS_URL)
        self.thread_parser = ThreadParser(page_to_parse=page_to_scrape)
        self.news_page_count = 1 if page_to_scrape == self.NEWS else news_page_count

    def scrape(self) -> list[Thread]:
        if self.page_to_scrape == self.NEWS:
            scraped_threads = self.scrape_news_pages()
        elif self.page_to_scrape == self.NEWEST:
            scraped_threads = self.scrape_newest_page()

        return self.create_or_update_threads(scraped_threads)

    def scrape_newest_page(self) -> list[ScrapedThreadData]:
        response = self.hn_request_session.get(f"{settings.HACKERNEWS_URL}newest")
        page = BeautifulSoup(response.text, "lxml")

        return self.thread_parser.parse(bs4_page_data=page)

    def scrape_news_pages(self) -> list[ScrapedThreadData]:
        scraped_threads = []
        for p_num in range(1, self.news_page_count + 1):
            sleep(0.5)

            response = self.hn_request_session.get(f"{settings.HACKERNEWS_URL}news?p={p_num}")
            page = BeautifulSoup(response.text, "lxml")

            page_scraped_threads = self.thread_parser.parse(bs4_page_data=page)
            scraped_threads.extend(page_scraped_threads)

        return scraped_threads

    def create_or_update_threads(self, scraped_threads: list[ScrapedThreadData]) -> list[Thread]:
        threads = []
        for scraped_thread in scraped_threads:
            thread, _ = Thread.objects.update_or_create(
                thread_id=scraped_thread["thread_id"], defaults=dict(scraped_thread)
            )
            threads.append(thread)

        return threads


class ThreadParser:
    """
    Parse threads from Hacker News /newest or /news page

    >>> parser = ThreadParser()
    >>> parser.parse(bs4_page_data=bs4_page_data)
    -> <list[ScrapedThreadData]>
    """

    def __init__(self, page_to_parse: str = ThreadScraper.NEWEST) -> None:
        self.page_to_parse = page_to_parse

    def parse(self, bs4_page_data: BeautifulSoup) -> list[ScrapedThreadData]:
        parsed_threads = []

        rows = bs4_page_data.find_all("tr")
        for row in rows:
            if isinstance(row.get("class"), list) and row.get("class")[0] == "athing":
                parsed_thread = self.parse_thread_data(data_row=row)
                parsed_threads.append(parsed_thread)

        return parsed_threads

    def parse_thread_data(self, data_row) -> ScrapedThreadData:
        thread_id = data_row.get("id")
        thread_title = data_row.find("span", class_="titleline").find("a").text

        # add whitespaces before and after thread title for full word matching
        thread_title_with_whitespaces = f" {thread_title} "

        story_link = data_row.find("span", class_="titleline").find("a").get("href")

        # hacker news post without url
        if "https://" not in story_link and "item?id=" in story_link:
            story_link = f"https://news.ycombinator.com/{story_link}"

        thread_meta_data = self.parse_thread_meta_data(meta_data_row=data_row.find_next_sibling())

        return ScrapedThreadData(
            thread_id=thread_id,
            title=thread_title_with_whitespaces,
            link=story_link,
            score=thread_meta_data.get("thread_score", 0),
            thread_created_at=thread_meta_data.get("thread_created_at", timezone.now()),
            comments_count=thread_meta_data.get("comments_count", 0),
            comments_link=thread_meta_data.get("comments_link"),
        )

    def parse_thread_meta_data(self, meta_data_row) -> ThreadMetaData:
        thread_score = 0
        if thread_score_span := meta_data_row.find("td", class_="subtext").find("span", class_="score"):
            thread_score = int("".join(i for i in thread_score_span.text if i.isdigit()))

        thread_created_at = timezone.now()
        if thread_created_at_span := meta_data_row.find("td", class_="subtext").find("span", class_="age"):
            thread_created_at = parser.parse(thread_created_at_span.get("title"))
            thread_created_at = thread_created_at.astimezone(tz.UTC)

        if self.page_to_parse == ThreadScraper.NEWS:
            comments_data_hyperlink = (
                meta_data_row.find("td", class_="subtext")
                .find("a", string="hide")
                .next_element.next_element.next_element
            )
        elif self.page_to_parse == ThreadScraper.NEWEST:
            comments_data_hyperlink = meta_data_row.find("a", class_="hnpast").next_element.next_element.next_element

        comments_count = 0
        if "comment" in comments_data_hyperlink.text:
            comments_count = [int(s) for s in comments_data_hyperlink.text.split() if s.isdigit()][0]

        try:
            comments_data_href = comments_data_hyperlink.get("href")
            comments_link = f"https://news.ycombinator.com/{comments_data_href}"
        except AttributeError:
            comments_link = None

        return ThreadMetaData(
            thread_score=thread_score,
            thread_created_at=thread_created_at,
            comments_count=comments_count,
            comments_link=comments_link,
        )
