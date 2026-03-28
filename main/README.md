# Intelligent App with Weaviate Query Agent

This project implements an intelligent e-commerce assistant over data in Weaviate Cloud.

It satisfies the assignment requirements by providing:
- At least 2 collections in Weaviate: `Products` and `Brands`
- Natural-language QA with Weaviate Query Agent
- Demo with 5 required query types
- Minimal CLI interface
- Optional extension with Transformation Agent

## Domain
E-commerce.

## Collections
1. `Products`
- `name` (TEXT)
- `category` (TEXT)
- `price` (NUMBER)
- `in_stock` (BOOL)
- `brand_name` (TEXT)
- `description` (TEXT)

2. `Brands`
- `brand_name` (TEXT)
- `country` (TEXT)
- `founded_year` (INT)
- `style_focus` (TEXT)
- `brand_story` (TEXT)

## Tech stack
- Python 3.10+
- `weaviate-client[agents]`
- Weaviate Cloud

## Setup
1. Create and activate virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` from `.env.example` and fill credentials:

- `WEAVIATE_URL`
- `WEAVIATE_API_KEY`
- `INFERENCE_PROVIDER_API_KEY` (Gemini API key)
- `GOOGLE_STUDIO_API_KEY` (optional, if you want explicit Google header)

## Run
### 1) Create schema + import seed data
```bash
python main.py setup
```

### Flask web interface
```bash
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

From the web UI you can:
- initialize collections and import data,
- ask natural-language questions,
- run the 5-query demo.

### 2) Run required Query Agent demo
```bash
python main.py demo
```

### 3) Ask custom question
```bash
python main.py ask "Recommend two in-stock items for rainy weather under 200 dollars"
```

### 4) Optional Transformation Agent demo (test data only)
```bash
python main.py transform
```

## Notes on security and reliability
- API keys are loaded only from environment variables.
- Basic error handling is included for config and runtime failures.
- Transformation Agent modifies objects in place. Use on test data only.

## Demo checklist (3-7 min)
- Show `.env` keys are configured.
- Run `python main.py setup`.
- Run `python main.py demo` and explain the 5 query types.
- Run one custom `ask` query.
- Optionally run `transform` and show workflow id/status.

## Project structure
- `main.py` entry point
- `src/config.py` env loading and validation
- `src/weaviate_client.py` cloud connection
- `src/data_loader.py` schema + import
- `src/query_assistant.py` Query Agent logic + demo prompts
- `src/transformation_extension.py` optional extension
- `src/cli.py` minimal user interface
- `data/` sample realistic collections
- `docs/report.md` short report template
