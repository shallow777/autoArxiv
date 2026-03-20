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
        digest = paper.digest
        code_link = str(digest.get("code_link", "")).strip()
        code_link_html = f' | <a href="{escape(code_link)}">Code</a>' if code_link else ""
        method = digest.get("method_overview", {})
        implications = digest.get("implications", {})
        figure = digest.get("most_important_figure", {})
        findings_html = "".join(
            f"<li><strong>{escape(str(item.get('title', 'Finding')))}:</strong> {escape(str(item.get('detail', '')))}</li>"
            for item in digest.get("key_findings", [])
        )
        research_questions_html = "".join(
            f"<li>{escape(str(item))}</li>"
            for item in digest.get("research_questions", [])
        )
        limitations_html = "".join(
            f"<li>{escape(str(item))}</li>"
            for item in digest.get("limitations", [])
        )
        items.append(
            f"""
            <section style="margin-bottom:24px;padding:16px;border:1px solid #d0d7de;border-radius:10px;">
              <h3 style="margin:0 0 8px 0;">{index}. {escape(paper.title)}</h3>
              <p style="margin:0 0 8px 0;"><strong>Topics:</strong> {escape(', '.join(digest.get('topics', paper.matched_topics)))}</p>
              <p style="margin:0 0 8px 0;"><strong>Authors:</strong> {escape(', '.join(paper.authors))}</p>
              <p style="margin:0 0 8px 0;"><strong>Venue / Year:</strong> {escape(str(digest.get('venue_or_year', paper.published.year)))}</p>
              <p style="margin:0 0 8px 0;">
                <strong>Links:</strong>
                <a href="{escape(paper.abs_url)}">Abstract</a> |
                <a href="{escape(paper.pdf_url)}">PDF</a>
                {code_link_html}
              </p>
              <h4 style="margin:12px 0 6px 0;">1. One-line takeaway</h4>
              <p style="margin:0 0 8px 0;">{escape(str(digest.get('one_line_takeaway', '')))}</p>
              <h4 style="margin:12px 0 6px 0;">2. Why it matters</h4>
              <p style="margin:0 0 8px 0;">{escape(str(digest.get('why_it_matters', '')))}</p>
              <h4 style="margin:12px 0 6px 0;">3. Research questions</h4>
              <ol style="margin:0 0 8px 18px;padding:0;">{research_questions_html}</ol>
              <h4 style="margin:12px 0 6px 0;">4. Background and problem setting</h4>
              <p style="margin:0 0 8px 0;">{escape(str(digest.get('background_and_problem_setting', '')))}</p>
              <h4 style="margin:12px 0 6px 0;">5. Method overview</h4>
              <p style="margin:0 0 8px 0;"><strong>Task / environment:</strong> {escape(str(method.get('task_environment', '')))}</p>
              <p style="margin:0 0 8px 0;"><strong>Condition / intervention design:</strong> {escape(str(method.get('condition_intervention_design', '')))}</p>
              <p style="margin:0 0 8px 0;"><strong>Evaluation metrics:</strong> {escape(str(method.get('evaluation_metrics', '')))}</p>
              <p style="margin:0 0 8px 0;"><strong>Model comparison:</strong> {escape(str(method.get('model_comparison', '')))}</p>
              <p style="margin:0 0 8px 0;"><strong>My understanding:</strong> {escape(str(method.get('my_understanding', '')))}</p>
              <h4 style="margin:12px 0 6px 0;">6. Key findings</h4>
              <ul style="margin:0 0 8px 18px;padding:0;">{findings_html}</ul>
              <h4 style="margin:12px 0 6px 0;">7. Most important figure</h4>
              <p style="margin:0 0 8px 0;"><strong>Figure source:</strong> {escape(str(figure.get('figure_source', '')))}</p>
              <p style="margin:0 0 8px 0;"><strong>Why this figure matters:</strong> {escape(str(figure.get('why_it_matters', '')))}</p>
              <p style="margin:0 0 8px 0;"><strong>How to read this figure:</strong> {escape(str(figure.get('how_to_read', '')))}</p>
              <h4 style="margin:12px 0 6px 0;">10. Implications for Agent / Skill / Memory</h4>
              <p style="margin:0 0 8px 0;"><strong>For Agent systems:</strong> {escape(str(implications.get('for_agent_systems', '')))}</p>
              <p style="margin:0 0 8px 0;"><strong>For Skill:</strong> {escape(str(implications.get('for_skill', '')))}</p>
              <p style="margin:0 0 8px 0;"><strong>For Memory:</strong> {escape(str(implications.get('for_memory', '')))}</p>
              <p style="margin:0 0 8px 0;"><strong>For evaluation:</strong> {escape(str(implications.get('for_evaluation', '')))}</p>
              <h4 style="margin:12px 0 6px 0;">11. Limitations</h4>
              <ul style="margin:0 0 8px 18px;padding:0;">{limitations_html}</ul>
              <h4 style="margin:12px 0 6px 0;">12. My take / Personal notes</h4>
              <p style="margin:0 0 8px 0;">{escape(str(digest.get('my_take', '')))}</p>
              <h4 style="margin:12px 0 6px 0;">13. Final summary</h4>
              <p style="margin:0 0 8px 0;">{escape(str(digest.get('final_summary', '')))}</p>
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
        digest = paper.digest
        code_link = str(digest.get("code_link", "")).strip()
        method = digest.get("method_overview", {})
        figure = digest.get("most_important_figure", {})
        implications = digest.get("implications", {})
        lines.extend(
            [
                f"## {index}. {paper.title}",
                "",
                f"**Topics:** {', '.join(digest.get('topics', paper.matched_topics))}",
                f"**Authors:** {', '.join(paper.authors)}",
                f"**Venue / Year:** {digest.get('venue_or_year', paper.published.year)}",
                f"**Links:** [Abstract]({paper.abs_url}) | [PDF]({paper.pdf_url})"
                + (f" | [Code]({code_link})" if code_link else ""),
                "",
                "### 1. One-line takeaway",
                "",
                str(digest.get("one_line_takeaway", "")),
                "",
                "### 2. Why it matters",
                "",
                str(digest.get("why_it_matters", "")),
                "",
                "### 3. Research questions",
                "",
                *[f"{idx}. {item}" for idx, item in enumerate(digest.get("research_questions", []), start=1)],
                "",
                "### 4. Background and problem setting",
                "",
                str(digest.get("background_and_problem_setting", "")),
                "",
                "### 5. Method overview",
                "",
                f"- Task / environment: {method.get('task_environment', '')}",
                f"- Condition / intervention design: {method.get('condition_intervention_design', '')}",
                f"- Evaluation metrics: {method.get('evaluation_metrics', '')}",
                f"- Model comparison: {method.get('model_comparison', '')}",
                f"- My understanding: {method.get('my_understanding', '')}",
                "",
                "### 6. Key findings",
                "",
                *[
                    f"- {item.get('title', 'Finding')}: {item.get('detail', '')}"
                    for item in digest.get("key_findings", [])
                ],
                "",
                "### 7. Most important figure",
                "",
                f"- Figure source: {figure.get('figure_source', '')}",
                f"- Why this figure matters: {figure.get('why_it_matters', '')}",
                f"- How to read this figure: {figure.get('how_to_read', '')}",
                "",
                "### 10. Implications for Agent / Skill / Memory",
                "",
                f"- For Agent systems: {implications.get('for_agent_systems', '')}",
                f"- For Skill: {implications.get('for_skill', '')}",
                f"- For Memory: {implications.get('for_memory', '')}",
                f"- For evaluation: {implications.get('for_evaluation', '')}",
                "",
                "### 11. Limitations",
                "",
                *[f"- {item}" for item in digest.get("limitations", [])],
                "",
                "### 12. My take / Personal notes",
                "",
                str(digest.get("my_take", "")),
                "",
                "### 13. Final summary",
                "",
                str(digest.get("final_summary", "")),
                "",
            ]
        )
    return "\n".join(lines)
