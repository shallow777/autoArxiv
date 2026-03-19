from __future__ import annotations

import json
import os

import requests

from .models import AppConfig, Paper


def enrich_papers(config: AppConfig, papers: list[Paper]) -> None:
    provider = os.getenv("LLM_PROVIDER", "").strip().lower() or "deepseek"
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    deepseek_model = os.getenv("DEEPSEEK_MODEL", "").strip() or "deepseek-chat"
    deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "").rstrip("/") or "https://api.deepseek.com"

    for paper in papers:
        if provider == "deepseek" and deepseek_key:
            paper.summary, paper.recommendation_reason = _summarize_with_deepseek(
                config=config,
                paper=paper,
                api_key=deepseek_key,
                model=deepseek_model,
                base_url=deepseek_base_url,
            )
        else:
            paper.summary, paper.recommendation_reason = _fallback_summary(paper)

def _summarize_with_deepseek(
    config: AppConfig,
    paper: Paper,
    api_key: str,
    model: str,
    base_url: str,
) -> tuple[str, str]:
    prompt = _build_prompt(config, paper)
    response = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You generate concise academic digests and must output valid JSON only.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    output_text = _extract_deepseek_text(data)
    return _parse_summary_payload(output_text)


def _build_prompt(config: AppConfig, paper: Paper) -> str:
    return (
        f"You are preparing a daily arXiv digest in {config.digest.language}.\n"
        "Return strict JSON with keys: summary, recommendation_reason.\n"
        "summary should be a concise paragraph covering problem, method, main findings, and why it matters.\n"
        "recommendation_reason should be one sentence explaining why this paper is worth reading for the matched topics.\n"
        "Base your answer on the paper content excerpt below, not on webpage structure or HTML.\n\n"
        f"Title: {paper.title}\n"
        f"Authors: {', '.join(paper.authors)}\n"
        f"Categories: {', '.join(paper.categories)}\n"
        f"Matched topics: {', '.join(paper.matched_topics)}\n"
        f"Abstract: {paper.abstract}\n\n"
        f"Paper content excerpt:\n{paper.article_text}\n"
    )

def _extract_deepseek_text(payload: dict) -> str:
    choices = payload.get("choices", [])
    if not choices:
        return ""
    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            text = item.get("text")
            if text:
                chunks.append(text)
        return "\n".join(chunks).strip()
    return ""


def _parse_summary_payload(output_text: str) -> tuple[str, str]:
    parsed = json.loads(output_text)
    return parsed["summary"].strip(), parsed["recommendation_reason"].strip()


def _fallback_summary(paper: Paper) -> tuple[str, str]:
    summary = (
        f"问题与目标：{paper.title}。"
        f" 核心内容：{paper.article_text[:600].rstrip()}..."
        f" 匹配主题：{', '.join(paper.matched_topics)}。"
    )
    reason = f"与 {', '.join(paper.matched_topics)} 相关，且关键词匹配分数为 {paper.relevance_score}。"
    return summary, reason
