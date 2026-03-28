from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

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


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")

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
        message = request.args.get("message", "")
        answer = request.args.get("answer", "")
        question = request.args.get("question", "")
        return render_template(
            "index.html",
            boot_error=boot_error,
            message=message,
            answer=answer,
            question=question,
            collections=[PRODUCTS_COLLECTION, BRANDS_COLLECTION],
        )

    @app.post("/setup")
    def setup_data():
        if app.config.get("BOOT_ERROR"):
            return redirect(url_for("home", message="Cannot run setup due to configuration error."))

        try:
            _ensure_data_ready(app, reset=True)
            return redirect(url_for("home", message="Setup complete. Collections are ready."))
        except Exception as exc:
            return redirect(url_for("home", message=f"Setup failed: {exc}"))

    @app.post("/ask")
    def ask_question():
        if app.config.get("BOOT_ERROR"):
            return redirect(url_for("home", message="Cannot query due to configuration error."))

        question = request.form.get("question", "").strip()
        if not question:
            return redirect(url_for("home", message="Please enter a question."))

        assistant = app.config["ASSISTANT"]
        try:
            _ensure_data_ready(app)
            response = assistant.ask(question)
            return redirect(
                url_for(
                    "home",
                    message="Answer generated.",
                    question=question,
                    answer=response.final_answer,
                )
            )
        except Exception as exc:
            return redirect(url_for("home", message=f"Query failed: {exc}", question=question))

    @app.post("/demo")
    def run_demo():
        if app.config.get("BOOT_ERROR"):
            return redirect(url_for("home", message="Cannot run demo due to configuration error."))

        assistant = app.config["ASSISTANT"]
        try:
            _ensure_data_ready(app)
            demo_items = assistant.run_required_demo()
            combined = "\n\n".join(
                f"{item.title}\nPrompt: {item.prompt}\nAnswer: {item.answer}"
                for item in demo_items
            )
            return redirect(url_for("home", message="Demo completed.", answer=combined))
        except Exception as exc:
            return redirect(url_for("home", message=f"Demo failed: {exc}"))

    return app


def run() -> None:
    app = create_app()
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=True)
