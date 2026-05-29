"""Command-line interface for ThinkGraph."""

from __future__ import annotations

import json
import sys

import click

from thinkgraph.analyzer import ThinkGraphAnalyzer


@click.group()
@click.version_option("0.1.0")
def main():
    """ThinkGraph — Reasoning Trace Analysis Framework."""


@main.command()
@click.option("--input", "-i", "input_file", required=True, help="Path to model output file")
@click.option("--model", "-m", default="unknown", help="Model name")
@click.option("--question", "-q", default="", help="Original question")
@click.option("--output", "-o", default="./output", help="Output directory")
@click.option("--json-output", is_flag=True, help="Print metrics as JSON")
def analyze(input_file, model, question, output, json_output):
    """Analyze a single model's reasoning trace."""
    text = _read_input(input_file)
    analyzer = ThinkGraphAnalyzer()
    result = analyzer.analyze(text, model_name=model, question=question)

    if json_output:
        click.echo(json.dumps(result.metrics, indent=2, ensure_ascii=False))
    else:
        click.echo(result.summary)

    paths = analyzer.visualize(result, output_dir=output)
    for key, path in paths.items():
        click.echo(f"  [{key}] {path}")


@main.command()
@click.option("--inputs", "-i", multiple=True, required=True, help="Model output files")
@click.option("--names", "-n", multiple=True, help="Model names (same order as inputs)")
@click.option("--question", "-q", default="", help="Shared question")
@click.option("--output", "-o", default="./output", help="Output directory")
def compare(inputs, names, question, output):
    """Compare reasoning traces across models."""
    if names and len(names) != len(inputs):
        click.echo("Error: --names count must match --inputs count", err=True)
        sys.exit(1)

    name_list = list(names) if names else [f"model_{i}" for i in range(len(inputs))]
    input_map = {}
    for name, path in zip(name_list, inputs):
        input_map[name] = _read_input(path)

    analyzer = ThinkGraphAnalyzer()
    comp = analyzer.compare(input_map, question=question)

    click.echo(f"\n=== Cross-Model Comparison ===")
    click.echo(f"Best model: {comp['best_model']}\n")
    click.echo(comp["metric_table"].to_string())
    click.echo("\nInsights:")
    for insight in comp["insights"]:
        click.echo(f"  • {insight}")

    import os
    os.makedirs(output, exist_ok=True)
    from thinkgraph.visualizer.report_viz import ReportVisualizer
    viz = ReportVisualizer()
    viz.plot_comparison_bar(comp, os.path.join(output, "comparison_bar.html"))
    click.echo(f"\nComparison chart saved to {output}/comparison_bar.html")


def _read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    main()
