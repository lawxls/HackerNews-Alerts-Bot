from datetime import datetime
from typing import TypedDict

from scraper.models import Comment


class ScrapedCommentData(TypedDict):
    comment_id: int
    parent_comment: Comment | None
    thread_id_int: int
    body: str
    username: str
    comment_created_at: datetime


class ScrapedThreadData(TypedDict):
    thread_id: int
    title: str
    thread_created_at: datetime
    creator_username: str | None
    score: int
    link: str
    comments_count: int
    comments_link: str | None


class ThreadMetaData(TypedDict):
    thread_score: int
    thread_created_at: datetime
    thread_creator_username: str | None
    comments_count: int
    comments_link: str | None
