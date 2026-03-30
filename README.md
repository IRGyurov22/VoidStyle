# Weaviate E-Commerce Query System - VoidStyle

A Python project that uses Weaviate Agents to answer natural-language questions about e-commerce products and brands.

## What this project does

- Builds and maintains two Weaviate collections: `Products` and `Brands`
- Imports seed data from JSON files with cleaning and validation
- Runs a Query Agent across both collections
- Supports CLI workflows for setup, demo queries, custom ask, and optional transformation
- Provides a Flask web UI for interactive usage

## Tech stack

- Python 3.10+
- Weaviate Cloud
- weaviate-client with Agents support
- Flask
- python-dotenv

## Project layout

```text
.
|-- app.py
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
        `-- index.html
```

## Installation

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root.

```env
WEAVIATE_URL=https://your-cluster-url.weaviate.network
WEAVIATE_API_KEY=your-weaviate-api-key
INFERENCE_PROVIDER_API_KEY=your-gemini-api-key

RESET_COLLECTIONS=false
```

Required variables:
- `WEAVIATE_URL`
- `WEAVIATE_API_KEY`
- `INFERENCE_PROVIDER_API_KEY`



## Web app usage

Run the Flask app:

```powershell
python app.py
```

Open in browser:
- `http://127.0.0.1:5000`

Available UI actions:
- Setup collections
- Run demo queries
- Ask custom natural-language questions

## Data model

### Products
- `name`
- `category`
- `price`
- `in_stock`
- `brand_name`
- `description`

### Brands
- `brand_name`
- `country`
- `founded_year`
- `style_focus`
- `brand_story`

## Data cleaning rules

During import, the loader performs:
- text normalization
- boolean coercion
- numeric parsing and bounds checks
- brand reference validation
- deduplication

This prevents malformed rows from entering the vectorized dataset.

## Common issues

Configuration error for missing environment variables:
- Confirm `.env` exists in project root.
- Confirm required keys are not empty.

Connection/auth errors:
- Verify Weaviate cluster URL and API key.
- Verify inference key is valid.

Unexpected empty answers:
- Run setup again.
- Confirm seed data files contain valid rows.

Transformation workflow concerns:
- Use transformation on test data only.

## Report

Detailed project report is available in:
- `docs/report.md`
