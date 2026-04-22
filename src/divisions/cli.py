"""Click-based CLI: `divisions lint`, `divisions show`, `divisions schema`."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
import yaml

from divisions.lint import format_issues, lint_tree
from divisions.models import Division
from divisions.paths import expected_path, parse_ocd_id


@click.group()
def main() -> None:
    """Tools for the curated OCD divisions dataset."""


@main.command()
@click.argument("path", type=click.Path(path_type=Path, exists=True), default="data")
def lint(path: Path) -> None:
    """Lint YAML files under PATH (default: data/)."""
    issues = lint_tree(path)
    if issues:
        click.echo(format_issues(issues), err=True)
        click.echo(f"\n{len(issues)} issue(s) found.", err=True)
        sys.exit(1)
    click.echo("ok")


@main.command()
@click.argument("file", type=click.Path(path_type=Path, exists=True))
def show(file: Path) -> None:
    """Load and print a division YAML as JSON (canonicalized)."""
    with file.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    div = Division.model_validate(raw)
    click.echo(div.model_dump_json(indent=2, exclude_none=True))


@main.command(name="path")
@click.argument("ocd_id")
def path_cmd(ocd_id: str) -> None:
    """Print the canonical file path for an OCD division id."""
    parse_ocd_id(ocd_id)  # validate
    click.echo(expected_path(ocd_id))


@main.command()
@click.option(
    "--out",
    type=click.Path(path_type=Path),
    default=Path("schema/division.schema.json"),
    help="Where to write the JSON schema.",
)
def schema(out: Path) -> None:
    """(Re)generate the JSON Schema from the pydantic models."""
    out.parent.mkdir(parents=True, exist_ok=True)
    js = Division.model_json_schema()
    out.write_text(json.dumps(js, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    click.echo(f"wrote {out}")


if __name__ == "__main__":
    main()
