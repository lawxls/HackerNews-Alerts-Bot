from datetime import datetime
from typing import TypedDict


class ScrapedCommentData(TypedDict):
    comment_id: int
    thread_id_int: int
    body: str
    username: str
    comment_created_at: datetime


class ScrapedThreadData(TypedDict):
    thread_id: int
    title: str
    thread_created_at: datetime
    score: int
    link: str
    comments_count: int
    comments_link: str | None


class ThreadMetaData(TypedDict):
    thread_score: int
    thread_created_at: datetime
    comments_count: int
    comments_link: str | None
