"""CLI entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from nullthread import __version__
from nullthread.ai.config import AISettings
from nullthread.analyze import analyze_ptx
from nullthread.passes.registry import PASS_NAMES
from nullthread.report import render_cli, render_html, render_json

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback()
def main_callback() -> None:
    """Nullthread — static analysis for GPU kernels (PTX)."""


@app.command("analyze")
def analyze_cmd(
    ptx_path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True, help="Path to .ptx file"),
    passes: str = typer.Option(
        ",".join(PASS_NAMES),
        "--passes",
        "-p",
        help=f"Comma-separated passes: {', '.join(PASS_NAMES)}",
    ),
    fmt: str = typer.Option(
        "cli",
        "--format",
        "-f",
        help="Output format: cli, json, html",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Write report to this file (recommended for json/html)",
    ),
    no_ai: bool = typer.Option(False, "--no-ai", help="Disable LLM diagnosis; use templates only"),
) -> None:
    """Analyze a PTX kernel and print or write a report."""
    names = [x.strip() for x in passes.split(",") if x.strip()]
    for n in names:
        if n not in PASS_NAMES:
            typer.echo(f"Unknown pass: {n}. Valid: {', '.join(PASS_NAMES)}", err=True)
            raise typer.Exit(code=2)

    cache_root = Path.cwd()
    result = analyze_ptx(
        ptx_path,
        pass_names=names,
        use_ai=not no_ai,
        ai_settings=AISettings(),
        cache_root=cache_root,
    )

    fmt_l = fmt.lower().strip()
    if fmt_l == "json":
        text = render_json(result)
    elif fmt_l == "html":
        text = render_html(result)
    elif fmt_l in ("cli", "text", "plain"):
        text = render_cli(result)
    else:
        typer.echo(f"Unknown format: {fmt}", err=True)
        raise typer.Exit(code=2)

    if output is not None:
        output.write_text(text, encoding="utf-8")
        typer.echo(f"Wrote {output}")
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")


@app.command("version")
def version_cmd() -> None:
    """Print version."""
    typer.echo(__version__)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
