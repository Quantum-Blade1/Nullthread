"""HTML report via Jinja2."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from nullthread.models import AnalysisResult


def render_html(result: AnalysisResult) -> str:
    tpl_dir = Path(__file__).resolve().parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(tpl_dir)),
        autoescape=select_autoescape(["html"]),
    )
    tpl = env.get_template("report.html")
    return tpl.render(result=result)
