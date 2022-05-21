from time import sleep

from bs4 import BeautifulSoup
from dateutil import parser, tz
from django.utils import timezone

from scraper.models import Thread
from scraper.types import ScrapedThread
from scraper.utils import start_request_session


class ThreadScraper:
    """
    Scrape and save threads from hackernews pages using BeautifulSoup

    >>> from scraper.scrape_threads import ThreadScraper
    >>> thread_scraper = ThreadScraper()
    >>> thread_scraper.scrape_and_save_threads()
    <list[Thread]>
    """

    HACKERNEWS_DOMEN = "https://news.ycombinator.com/"

    def __init__(self):
        return

    def scrape_and_save_threads(self, page_count: int = 10) -> list[Thread]:

        hn_session = start_request_session(domen=self.HACKERNEWS_DOMEN)

        threads = []
        for p_num in range(1, page_count + 1):
            sleep(0.5)

            page_request = hn_session.get(f"{self.HACKERNEWS_DOMEN}news?p={p_num}")
            page = BeautifulSoup(page_request.text, "lxml")

            rows = page.find_all("tr")
            for row in rows:
                if isinstance(row.get("class"), list) and row.get("class")[0] == "athing":

                    data_row = row

                    scraped_thread = self.parse_data(data_row=data_row)
                    thread = self.create_or_update_thread(scraped_thread=scraped_thread)
                    threads.append(thread)

        return threads

    def parse_data(self, data_row) -> ScrapedThread:

        thread_id = data_row.get("id")
        thread_title = data_row.find("a", class_="titlelink").text
        story_link = data_row.find("a", class_="titlelink").get("href")

        meta_data_row = data_row.find_next_sibling()

        thread_score = 0
        if thread_score_span := meta_data_row.find("td", class_="subtext").find(
            "span", class_="score"
        ):
            thread_score = int(thread_score_span.text.replace(" points", ""))

        thread_created_at = timezone.now()
        if thread_created_at_span := meta_data_row.find("td", class_="subtext").find(
            "span", class_="age"
        ):
            thread_created_at = parser.parse(thread_created_at_span.get("title"))
            thread_created_at = thread_created_at.astimezone(tz.UTC)

        comments_data_hyperlink = (
            meta_data_row.find("td", class_="subtext")
            .find("a", string="hide")
            .next_element.next_element.next_element
        )

        comments_count = 0
        if "comment" in comments_data_hyperlink.text:
            comments_count = [int(s) for s in comments_data_hyperlink.text.split() if s.isdigit()][
                0
            ]

        try:
            comments_data_href = comments_data_hyperlink.get("href")
            comments_link = f"https://news.ycombinator.com/{comments_data_href}"
        except AttributeError:
            comments_link = None

        return ScrapedThread(
            thread_id=thread_id,
            title=thread_title,
            link=story_link,
            score=thread_score,
            thread_created_at=thread_created_at,
            comments_count=comments_count,
            comments_link=comments_link,
        )

    def create_or_update_thread(self, scraped_thread: ScrapedThread) -> Thread:

        scraped_thread_dict = dict(scraped_thread)

        thread, _ = Thread.objects.update_or_create(
            thread_id=scraped_thread_dict.get("thread_id"), defaults=scraped_thread_dict
        )

        return thread
