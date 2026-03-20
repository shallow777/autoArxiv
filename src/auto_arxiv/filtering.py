from __future__ import annotations

from .models import AppConfig, Paper, TopicRule


def select_papers(config: AppConfig, papers: list[Paper], seen_ids: set[str]) -> list[Paper]:
    selected: list[Paper] = []
    for paper in papers:
        if paper.arxiv_id in seen_ids:
            continue

        matched_topics: list[str] = []
        total_score = 0
        for topic in config.topics:
            score = _score_topic_match(paper, topic)
            if score > 0:
                matched_topics.append(topic.name)
                total_score += score

        if not matched_topics:
            continue

        paper.matched_topics = matched_topics
        paper.relevance_score = total_score
        selected.append(paper)

    selected.sort(key=lambda item: (-item.relevance_score, -item.published.timestamp()))
    return selected[: config.digest.max_papers_per_run]


def _score_topic_match(paper: Paper, topic: TopicRule) -> int:
    title = paper.title.lower()
    abstract = paper.abstract.lower()
    text = f"{title}\n{abstract}"
    categories = set(paper.categories)

    if topic.categories and not categories.intersection(topic.categories):
        return 0

    if any(keyword in text for keyword in topic.exclude_keywords):
        return 0

    for group in topic.required_keyword_groups:
        if not any(keyword in text for keyword in group):
            return 0

    score = 0
    for keyword in topic.include_keywords:
        if keyword in title:
            score += 4
        elif keyword in abstract:
            score += 2

    if categories.intersection(topic.categories):
        score += 1

    return score
