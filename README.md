# Weaviate E-Commerce Query System - VoidStyle

VoidStyle is a Python + Weaviate Agents project that answers natural-language e-commerce questions over product and brand data.

## What the current project includes

- Two Weaviate collections: `Products` and `Brands`
- Seed import from local JSON with cleaning, validation, and deduplication
- Query Agent configured across both collections
- Flask UI with setup, demo, ask, and session-based chat history
- Optional Transformation Agent workflow for product auto-tags

## Tech stack

- Python 3.10+
- Weaviate Cloud
- `weaviate-client[agents]`
- Flask
- python-dotenv

## Project layout

```text
.
|-- app.py
|-- README.md
|-- requirements.txt
|-- data/
|   |-- brands.json
|   `-- products.json
|-- docs/
|   `-- report.md
`-- src/
        |-- cli.py
        |-- config.py
        |-- data_loader.py
        |-- flask_app.py
        |-- query_assistant.py
        |-- transformation_extension.py
        |-- weaviate_client.py
        `-- templates/
                |-- agent.html
                `-- index.html
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

Create `.env` in the project root:

```env
WEAVIATE_URL=https://your-cluster-url.weaviate.network
WEAVIATE_API_KEY=your-weaviate-api-key
INFERENCE_PROVIDER_API_KEY=your-inference-key

# Optional
GOOGLE_STUDIO_API_KEY=your-google-studio-key
RESET_COLLECTIONS=false
FLASK_SECRET_KEY=change-this-in-production
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

Required variables:

- `WEAVIATE_URL`
- `WEAVIATE_API_KEY`
- `INFERENCE_PROVIDER_API_KEY`

Notes:

- If `GOOGLE_STUDIO_API_KEY` is empty, the app falls back to `INFERENCE_PROVIDER_API_KEY`.
- `RESET_COLLECTIONS` is used by CLI setup; the web setup route always resets before import.

## Run the app

```powershell
python app.py
```

Default URL: `http://127.0.0.1:5000`

## Web UI behavior

- `GET /`: landing page
- `GET /agent`: chat page
- `POST /setup`: reset collections, recreate schema, and re-seed data
- `POST /ask`: ask a question (includes prior chat turns in the prompt)
- `POST /demo`: run the 5-query required demo and store output in chat
- `POST /new-chat`: clear session chat history

Chat history is stored in Flask session and capped at 12 turns.

## CLI module status

`src/cli.py` contains setup/demo/ask/transform commands and a `main()` function. It currently does not expose a direct `if __name__ == "__main__":` entrypoint.

If you still want to invoke it directly, you can run:

```powershell
python -c "from src.cli import main; main()" setup
python -c "from src.cli import main; main()" demo
python -c "from src.cli import main; main()" ask "What shoes are in stock under 80?"
python -c "from src.cli import main; main()" transform
```

## Data model

### Products

- `name` (TEXT)
- `category` (TEXT)
- `price` (NUMBER)
- `in_stock` (BOOL)
- `brand_name` (TEXT)
- `description` (TEXT)

### Brands

- `brand_name` (TEXT)
- `country` (TEXT)
- `founded_year` (INT)
- `style_focus` (TEXT)
- `brand_story` (TEXT)

## Import and cleaning logic

During seed import (`src/data_loader.py`):

- normalize text (trim + collapse whitespace)
- coerce booleans for `in_stock`
- validate numeric ranges:
    - `price >= 0`
    - `1800 <= founded_year <= 2100`
- reject products whose `brand_name` is not in cleaned brands
- deduplicate:
    - brands by `brand_name`
    - products by (`name`, `brand_name`)

Data is inserted only if the target collection is currently empty.

## Seed data snapshot

- `data/products.json`: 108 records
- `data/brands.json`: 31 records

## Common issues

Missing env variables:

- Confirm `.env` exists and required keys are non-empty.

Connection/auth errors:

- Verify `WEAVIATE_URL` and `WEAVIATE_API_KEY`.
- Verify inference key values.

Empty or weak answers:

- Run setup from the UI to force a fresh reset and re-seed.
- Confirm seed JSON still contains valid objects.

Transformation workflow caveat:

- Treat transformation as optional/test workflow and validate output before production use.

## Report

Detailed project report: `docs/report.md`
