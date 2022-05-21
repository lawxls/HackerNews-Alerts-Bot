from datetime import datetime
from typing import TypedDict


class ScrapedThread(TypedDict):
    thread_id: int
    title: str
    thread_created_at: datetime
    score: int
    link: str
    comments_count: int
    comments_link: str | None
