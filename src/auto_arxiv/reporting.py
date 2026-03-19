from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path

from .models import AppConfig, Paper


def write_report(reports_dir: str | Path, config: AppConfig, papers: list[Paper]) -> Path:
    output_dir = Path(reports_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_date = datetime.utcnow().strftime("%Y-%m-%d")
    path = output_dir / f"{report_date}.md"
    path.write_text(_render_markdown(config, papers), encoding="utf-8")
    return path


def render_email_html(config: AppConfig, papers: list[Paper]) -> str:
    items = []
    for index, paper in enumerate(papers, start=1):
        items.append(
            f"""
            <section style="margin-bottom:24px;padding:16px;border:1px solid #d0d7de;border-radius:10px;">
              <h3 style="margin:0 0 8px 0;">{index}. {escape(paper.title)}</h3>
              <p style="margin:0 0 8px 0;"><strong>Topics:</strong> {escape(', '.join(paper.matched_topics))}</p>
              <p style="margin:0 0 8px 0;"><strong>Why read:</strong> {escape(paper.recommendation_reason)}</p>
              <p style="margin:0 0 8px 0;">{escape(paper.summary)}</p>
              <p style="margin:0;">
                <a href="{escape(paper.abs_url)}">Abstract</a>
                |
                <a href="{escape(paper.pdf_url)}">PDF</a>
              </p>
            </section>
            """
        )

    body = "\n".join(items) if items else "<p>No new matching papers were found in this run.</p>"
    return f"""
    <html>
      <body style="font-family:Arial,sans-serif;max-width:860px;margin:0 auto;padding:24px;line-height:1.6;color:#24292f;">
        <h1>{escape(config.digest.project_name)}</h1>
        <p>Matched papers: {len(papers)}</p>
        {body}
      </body>
    </html>
    """


def _render_markdown(config: AppConfig, papers: list[Paper]) -> str:
    lines = [
        f"# {config.digest.project_name}",
        "",
        f"- Generated at: {datetime.utcnow().isoformat()}Z",
        f"- Matched papers: {len(papers)}",
        "",
    ]
    if not papers:
        lines.append("No new matching papers were found.")
        lines.append("")
        return "\n".join(lines)

    for index, paper in enumerate(papers, start=1):
        lines.extend(
            [
                f"## {index}. {paper.title}",
                "",
                f"- arXiv ID: `{paper.arxiv_id}`",
                f"- Topics: {', '.join(paper.matched_topics)}",
                f"- Why read: {paper.recommendation_reason}",
                f"- Abstract: {paper.abs_url}",
                f"- PDF: {paper.pdf_url}",
                "",
                paper.summary,
                "",
            ]
        )
    return "\n".join(lines)
