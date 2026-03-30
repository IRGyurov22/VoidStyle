from __future__ import annotations

from html import escape
import os
from pathlib import Path
import re

from flask import Flask, redirect, render_template, request, session, url_for

from src.config import load_settings
from src.data_loader import (
    BRANDS_COLLECTION,
    PRODUCTS_COLLECTION,
    ensure_schema,
    import_seed_data,
    reset_collections,
)
from src.query_assistant import WeaviateQueryAssistant
from src.weaviate_client import connect


NUMBERED_ITEM_RE = re.compile(r"^\s*\d+\.\s+(.+)$")
PRICE_RE = re.compile(r"(Price:\s*\$?\d+(?:\.\d{2})?)")
CHAT_HISTORY_KEY = "chat_history"
MAX_CHAT_TURNS = 12


def format_answer_for_display(answer: str) -> str:
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    if not lines:
        return ""

    intro_lines: list[str] = []
    items: list[str] = []
    outro_lines: list[str] = []
    in_list = False

    for line in lines:
        match = NUMBERED_ITEM_RE.match(line)
        if match:
            in_list = True
            item_html = escape(match.group(1))
            item_html = PRICE_RE.sub(r'<span class="answer-price">\\1</span>', item_html)
            items.append(item_html)
            continue

        if in_list:
            outro_lines.append(escape(line))
        else:
            intro_lines.append(escape(line))

    if not items:
        return "<p class=\"answer-plain\">" + "<br>".join(intro_lines) + "</p>"

    html_parts: list[str] = []
    if intro_lines:
        html_parts.append("<p class=\"answer-intro\">" + " ".join(intro_lines) + "</p>")

    html_parts.append("<ol class=\"answer-list\">")
    html_parts.extend(f"<li>{item}</li>" for item in items)
    html_parts.append("</ol>")

    if outro_lines:
        html_parts.append("<p class=\"answer-outro\">" + " ".join(outro_lines) + "</p>")

    return "".join(html_parts)


def _bootstrap_runtime():
    settings = load_settings()
    client = connect(settings)
    assistant = WeaviateQueryAssistant(client)
    data_dir = Path(__file__).resolve().parent.parent / "data"
    return settings, client, assistant, data_dir


def _ensure_data_ready(app: Flask, reset: bool = False) -> None:
    client = app.config["CLIENT"]
    data_dir = app.config["DATA_DIR"]

    if reset:
        reset_collections(client)

    ensure_schema(client)
    import_seed_data(client, data_dir)


def _get_chat_history() -> list[dict[str, str]]:
    raw_history = session.get(CHAT_HISTORY_KEY, [])
    history: list[dict[str, str]] = []
    if not isinstance(raw_history, list):
        return history

    for turn in raw_history:
        if not isinstance(turn, dict):
            continue
        question = str(turn.get("question", "")).strip()
        answer = str(turn.get("answer", "")).strip()
        if not question or not answer:
            continue
        history.append({"question": question, "answer": answer})
    return history


def _store_chat_history(history: list[dict[str, str]]) -> None:
    session[CHAT_HISTORY_KEY] = history[-MAX_CHAT_TURNS:]


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "voidstyle-dev-key")

    try:
        settings, client, assistant, data_dir = _bootstrap_runtime()
    except Exception as exc:
        app.config["BOOT_ERROR"] = str(exc)
        settings, client, assistant, data_dir = None, None, None, None

    app.config["SETTINGS"] = settings
    app.config["CLIENT"] = client
    app.config["ASSISTANT"] = assistant
    app.config["DATA_DIR"] = data_dir

    @app.get("/")
    def home():
        boot_error = app.config.get("BOOT_ERROR")
        return render_template("index.html", boot_error=boot_error)

    @app.get("/agent")
    def agent_page():
        boot_error = app.config.get("BOOT_ERROR")
        message = request.args.get("message", "")
        pending_question = request.args.get("question", "")
        chat_history = [
            {
                "question": turn["question"],
                "answer": turn["answer"],
                "formatted_answer": format_answer_for_display(turn["answer"]),
            }
            for turn in _get_chat_history()
        ]
        return render_template(
            "agent.html",
            boot_error=boot_error,
            message=message,
            pending_question=pending_question,
            chat_history=chat_history,
            collections=[PRODUCTS_COLLECTION, BRANDS_COLLECTION],
        )

    @app.post("/setup")
    def setup_data():
        if app.config.get("BOOT_ERROR"):
            return redirect(url_for("agent_page", message="Cannot run setup due to configuration error."))

        try:
            _ensure_data_ready(app, reset=True)
            return redirect(url_for("agent_page", message="Setup complete. Collections are ready."))
        except Exception as exc:
            return redirect(url_for("agent_page", message=f"Setup failed: {exc}"))

    @app.post("/ask")
    def ask_question():
        if app.config.get("BOOT_ERROR"):
            return redirect(
                url_for("agent_page", message="Cannot query due to configuration error.", _anchor="composer-anchor")
            )

        question = request.form.get("question", "").strip()
        if not question:
            return redirect(url_for("agent_page", message="Please enter a question.", _anchor="composer-anchor"))

        assistant = app.config["ASSISTANT"]
        try:
            _ensure_data_ready(app)
            history = _get_chat_history()

            conversation: list[dict[str, str]] = []
            for turn in history:
                conversation.append({"role": "user", "content": turn["question"]})
                conversation.append({"role": "assistant", "content": turn["answer"]})
            conversation.append({"role": "user", "content": question})

            response = assistant.ask(conversation)
            history.append({"question": question, "answer": response.final_answer})
            _store_chat_history(history)
            return redirect(
                url_for(
                    "agent_page",
                    message="Answer generated.",
                    _anchor="composer-anchor",
                )
            )
        except Exception as exc:
            return redirect(
                url_for(
                    "agent_page",
                    message=f"Query failed: {exc}",
                    question=question,
                    _anchor="composer-anchor",
                )
            )

    @app.post("/demo")
    def run_demo():
        if app.config.get("BOOT_ERROR"):
            return redirect(url_for("agent_page", message="Cannot run demo due to configuration error."))

        assistant = app.config["ASSISTANT"]
        try:
            _ensure_data_ready(app)
            demo_items = assistant.run_required_demo()
            combined = "\n\n".join(
                f"{item.title}\nPrompt: {item.prompt}\nAnswer: {item.answer}"
                for item in demo_items
            )
            history = _get_chat_history()
            history.append({"question": "Run 5-query demo", "answer": combined})
            _store_chat_history(history)
            return redirect(url_for("agent_page", message="Demo completed."))
        except Exception as exc:
            return redirect(url_for("agent_page", message=f"Demo failed: {exc}"))

    @app.post("/new-chat")
    def new_chat():
        session.pop(CHAT_HISTORY_KEY, None)
        return redirect(url_for("agent_page", message="Started a new chat."))

    return app


def run() -> None:
    app = create_app()
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=True)
