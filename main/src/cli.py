from __future__ import annotations

import argparse
from pathlib import Path

from src.config import load_settings
from src.data_loader import ensure_schema, import_seed_data, reset_collections
from src.query_assistant import WeaviateQueryAssistant, format_search_preview
from src.transformation_extension import run_transformation_demo
from src.weaviate_client import connect


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Weaviate Query Agent demo app (e-commerce domain)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("setup", help="Create collections and import seed data.")
    sub.add_parser("demo", help="Run the required 5-query Query Agent demo.")

    ask_parser = sub.add_parser("ask", help="Ask one custom natural language question.")
    ask_parser.add_argument("question", type=str, help="Question to send to Query Agent")

    sub.add_parser(
        "transform", help="Optional Transformation Agent demo (test data only)."
    )
    return parser


def cmd_setup(client, data_dir: Path, reset: bool) -> None:
    if reset:
        reset_collections(client)
    ensure_schema(client)
    import_seed_data(client, data_dir)
    print("Setup complete. Collections: Products, Brands")


def cmd_demo(client) -> None:
    assistant = WeaviateQueryAssistant(client)

    search_mode_query = "Find vintage style products under 100 dollars."
    search_response = assistant.search(search_mode_query, limit=5)
    print("\\n=== Search mode preview ===")
    print(f"Prompt: {search_mode_query}")
    print(format_search_preview(search_response))

    print("\\n=== Ask mode required demo (5 queries) ===")
    for item in assistant.run_required_demo():
        print(f"\\n{item.title}")
        print(f"Prompt: {item.prompt}")
        print(f"Answer: {item.answer}")


def cmd_ask(client, question: str) -> None:
    assistant = WeaviateQueryAssistant(client)
    response = assistant.ask(question)
    print("\\n=== Agent answer ===")
    print(response.final_answer)


def cmd_transform(client) -> None:
    workflow_id, status = run_transformation_demo(client)
    print("Transformation workflow started.")
    print(f"workflow_id: {workflow_id}")
    print(f"status: {status}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        settings = load_settings()
    except ValueError as exc:
        print(f"Configuration error: {exc}")
        return

    client = connect(settings)
    data_dir = Path(__file__).resolve().parent.parent / "data"

    try:
        if args.command == "setup":
            cmd_setup(client, data_dir=data_dir, reset=settings.reset_collections)
        elif args.command == "demo":
            cmd_demo(client)
        elif args.command == "ask":
            cmd_ask(client, question=args.question)
        elif args.command == "transform":
            cmd_transform(client)
        else:
            parser.print_help()
    except Exception as exc:
        print(f"Runtime error: {exc}")
    finally:
        client.close()
