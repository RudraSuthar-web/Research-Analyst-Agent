"""
main.py
CLI entry point for the AI Research Analyst Agent.

Usage:
  python main.py ingest pdf path/to/paper.pdf --tags ai,nlp
  python main.py ingest url https://arxiv.org/abs/... --tags transformers
  python main.py ask "What are the main contributions of the attention paper?"
  python main.py ask "Latest news on LLMs" --web
  python main.py list
"""
import argparse
import sys

from rich.console import Console
from rich.table import Table

from storage.database import get_session, Document as DBDocument

console = Console()


def cmd_ingest(args):
    from ingestion.pipeline import ingest_pdf, ingest_url
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
    if args.type == "pdf":
        ingest_pdf(args.source, tags=tags)
    elif args.type == "url":
        ingest_url(args.source, tags=tags)
    else:
        console.print("[red]Unknown type. Use 'pdf' or 'url'.[/red]")
        sys.exit(1)


def cmd_list(args):
    with get_session() as session:
        docs = session.query(DBDocument).order_by(DBDocument.created_at.desc()).all()

    if not docs:
        console.print("[yellow]No documents ingested yet.[/yellow]")
        return

    table = Table(title="Ingested Documents", show_lines=True)
    table.add_column("ID",      style="dim",   width=10)
    table.add_column("Title",   style="bold",  width=36)
    table.add_column("Type",    width=6)
    table.add_column("Chunks",  justify="right", width=7)
    table.add_column("Tags",    width=20)
    table.add_column("Ingested",              width=12)

    for doc in docs:
        table.add_row(
            doc.id[:8] + "...",
            doc.title[:35],
            doc.source_type,
            str(doc.chunk_count),
            ", ".join(doc.tags or []),
            doc.created_at.strftime("%Y-%m-%d"),
        )
    console.print(table)


def cmd_ask(args):
    from agent.graph import run_agent

    console.print(f"\n[bold cyan]Query:[/bold cyan] {args.query}\n")
    console.rule("[dim]Agent running[/dim]")

    # The synthesizer_node now handles streaming the answer directly to console
    run_agent(args.query, force_web_search=args.web)


def build_parser():
    parser = argparse.ArgumentParser(
        description="AI Research Analyst Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    # ingest
    p_ingest = sub.add_parser("ingest", help="Ingest a document")
    p_ingest.add_argument("type",   choices=["pdf", "url"])
    p_ingest.add_argument("source", help="File path or URL")
    p_ingest.add_argument("--tags", default="", help="Comma-separated tags")

    # list
    sub.add_parser("list", help="List all ingested documents")

    # ask
    p_ask = sub.add_parser("ask", help="Ask a research question")
    p_ask.add_argument("query", help="Your research question")
    p_ask.add_argument("--web", action="store_true",
                       help="Force web search in addition to KB lookup")

    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "ask":
        cmd_ask(args)
    else:
        parser.print_help()
