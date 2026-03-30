# Project Report: Weaviate E-Commerce Query System (VoidStyle)

## 1. Project Goal
VoidStyle is an e-commerce assistant that uses Weaviate Agents to answer natural-language questions over product and brand data.

Primary goals in the current implementation:

- Build a reproducible ingestion pipeline from local JSON to Weaviate collections.
- Support cross-collection natural-language querying (`Products` + `Brands`).
- Provide an interactive Flask interface for setup, asking questions, and running a required 5-query demo.
- Keep transformation support available as an optional extension.

## 2. Current Architecture

The project is organized into four practical layers.

### 2.1 Configuration Layer

- Module: `src/config.py`
- Loads `.env` values via `python-dotenv`.
- Validates required settings at startup.

Required environment variables:

- `WEAVIATE_URL`
- `WEAVIATE_API_KEY`
- `INFERENCE_PROVIDER_API_KEY`

Optional variables currently used:

- `GOOGLE_STUDIO_API_KEY`
- `RESET_COLLECTIONS` (default `false`)
- `FLASK_SECRET_KEY` (default `voidstyle-dev-key`)
- `FLASK_HOST` (default `127.0.0.1`)
- `FLASK_PORT` (default `5000`)

### 2.2 Data + Schema Layer

- Module: `src/data_loader.py`
- Collections:
  - `Products`
  - `Brands`
- Vectorizer: `text2vec_google_gemini`
- Seed files:
  - `data/products.json` (108 raw records)
  - `data/brands.json` (31 raw records)

### 2.3 Agent Layer

- Query Agent wrapper: `src/query_assistant.py`
  - Uses `weaviate.agents.query.QueryAgent`
  - Queries both collections in one context
  - Supports ask, search preview, and required demo prompts
- Transformation extension: `src/transformation_extension.py` (optional)
  - Uses `TransformationAgent`
  - Appends `auto_tags` to product objects
  - Returns `workflow_id` and status

### 2.4 Interface Layer

- Flask app entrypoint: `app.py` -> `src/flask_app.py`
- Templates:
  - `src/templates/index.html`
  - `src/templates/agent.html`
- CLI module exists in `src/cli.py` with commands (`setup`, `demo`, `ask`, `transform`) and `main()`.
  - Note: no direct `if __name__ == "__main__":` entrypoint is present right now.

## 3. Data Model

### 3.1 Products

- `name` (TEXT)
- `category` (TEXT)
- `price` (NUMBER)
- `in_stock` (BOOL)
- `brand_name` (TEXT)
- `description` (TEXT)

### 3.2 Brands

- `brand_name` (TEXT)
- `country` (TEXT)
- `founded_year` (INT)
- `style_focus` (TEXT)
- `brand_story` (TEXT)

## 4. Ingestion and Data Quality Behavior

The seed importer is defensive and normalizes data before insertion.

Implemented cleaning steps:

- Normalize all text values (trim + collapse internal whitespace).
- Normalize category/style casing to lowercase.
- Coerce booleans for `in_stock` from common text variants.
- Parse and validate numerics:
  - `price >= 0`
  - `1800 <= founded_year <= 2100`
- Validate cross-reference integrity:
  - products are accepted only if `brand_name` exists in cleaned brands
- Deduplicate:
  - brands by `brand_name`
  - products by (`name`, `brand_name`)

Import behavior:

- Create collections if missing.
- Insert seed data only when collection count is zero.
- Full reset support exists via `reset_collections()`.

## 5. Query Behavior and Demo Coverage

The Query Agent is initialized with a system prompt that prioritizes grounded answers and transparency when information is missing.

Supported interaction styles:

- Single question ask mode.
- Search mode (`assistant.search`) with object preview formatting.
- Conversation-style prompts (list of user/assistant turns).
- Aggregation-like natural-language requests.

Required demo prompts implemented in code:

1. Normal search
2. Multi-collection query
3. Follow-up prompt
4. Filtering/aggregation-like question
5. Free-form user request

## 6. Flask Runtime Flow

Startup flow:

1. Load settings and validate required env vars.
2. Connect to Weaviate Cloud with API-key auth.
3. Build a reusable Query Assistant.
4. Keep references (`settings`, `client`, `assistant`, `data_dir`) in app config.

Route behavior:

- `GET /`: home page, includes boot-error banner when startup fails.
- `GET /agent`: agent page + rendered chat history.
- `POST /setup`: always resets collections, then ensures schema + imports seed data.
- `POST /ask`: ensures schema/import (non-reset), builds conversation from session history, asks Query Agent, stores answer.
- `POST /demo`: runs required 5-query demo and appends combined output to chat history.
- `POST /new-chat`: clears chat history from session.

Chat/session behavior:

- Session key: `chat_history`
- Max stored turns: 12
- Assistant answers are HTML-formatted for numbered list readability.

## 7. Strengths in Current State

- Clear separation between config, ingestion, retrieval logic, and UI.
- Safe and repeatable setup path through schema checks and seed import controls.
- Multi-collection Query Agent setup matches the e-commerce domain.
- Session-backed conversational flow improves continuity in web usage.

## 8. Current Limitations

- CLI functionality is implemented but lacks a direct script entrypoint guard.
- Query quality depends on model and dataset coverage.
- Aggregation-like answers are LLM-generated reasoning, not deterministic SQL metrics.
- Transformation flow is optional and best treated as experimental/test workflow.
- No automated test suite yet.

## 9. Recommended Next Improvements

- Add `if __name__ == "__main__": main()` in `src/cli.py` for direct CLI execution.
- Add unit tests for cleaning/validation and integration tests for setup/query paths.
- Add structured observability (timings, request IDs, failure classification).
- Persist chat history beyond session memory when needed.
- Add evaluation harness for relevance/groundedness.

## 10. Conclusion

The current codebase delivers a working end-to-end AI retrieval assistant over e-commerce data using Weaviate Agents. It combines robust seed-data cleaning, cross-collection querying, and an interactive Flask interface, while leaving clear extension points for testing, observability, and production hardening.
