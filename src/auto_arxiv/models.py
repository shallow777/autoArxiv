from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class TopicRule:
    name: str
    categories: list[str]
    include_keywords: list[str]
    exclude_keywords: list[str]


@dataclass(slots=True)
class DigestSettings:
    project_name: str
    lookback_days: int
    max_papers_per_run: int
    max_candidates: int
    language: str


@dataclass(slots=True)
class AppConfig:
    digest: DigestSettings
    topics: list[TopicRule]


@dataclass(slots=True)
class Paper:
    arxiv_id: str
    title: str
    abstract: str
    article_text: str
    published: datetime
    updated: datetime
    authors: list[str]
    categories: list[str]
    abs_url: str
    pdf_url: str
    matched_topics: list[str] = field(default_factory=list)
    relevance_score: int = 0
    summary: str = ""
    recommendation_reason: str = ""
