# Project Report: Weaviate E-Commerce Query System

## 1. Goal
This project delivers an intelligent e-commerce assistant that answers natural-language questions using Weaviate Agents over structured product and brand data.

Core objectives:
- Build a reproducible pipeline from local JSON data to searchable Weaviate collections.
- Support user-friendly natural-language querying across multiple collections.
- Demonstrate follow-up and context-aware questioning.
- Provide both CLI and web interfaces for setup and interaction.
- Include an optional transformation workflow for data enrichment.

## 2. Architecture Overview
The system is organized into three layers.

### 2.1 Data Layer
- Storage and retrieval: Weaviate Cloud
- Collections:
	- `Products`
	- `Brands`
- Vectorization: `text2vec_google_gemini`
- Seed input files:
	- `data/products.json`
	- `data/brands.json`

### 2.2 Agent Layer
- Query Agent (`weaviate.agents.query.QueryAgent`)
	- Processes natural-language prompts.
	- Queries both `Products` and `Brands` in one assistant context.
	- Supports normal prompts, follow-up prompts, and broad free-form requests.
- Transformation Agent (`weaviate.agents.transformation.TransformationAgent`, optional)
	- Adds `auto_tags` to product objects.
	- Runs asynchronously and returns `workflow_id` and status.

### 2.3 Interface Layer
- CLI interface (`src/cli.py`):
	- `setup`, `demo`, `ask`, `transform`
- Flask web interface (`app.py`, `src/flask_app.py`):
	- Setup action
	- Ask action
	- Demo action

## 3. Data Model

### 3.1 Products collection
Fields:
- `name` (TEXT)
- `category` (TEXT)
- `price` (NUMBER)
- `in_stock` (BOOL)
- `brand_name` (TEXT)
- `description` (TEXT)

### 3.2 Brands collection
Fields:
- `brand_name` (TEXT)
- `country` (TEXT)
- `founded_year` (INT)
- `style_focus` (TEXT)
- `brand_story` (TEXT)

## 4. Ingestion and Data Quality Logic
The ingestion pipeline is intentionally defensive to improve retrieval quality.

Implemented steps:
- Read JSON from local files.
- Normalize text values (trim and collapse whitespace).
- Coerce booleans (`in_stock`) from common string forms.
- Validate numeric fields and bounds:
	- `price >= 0`
	- `1800 <= founded_year <= 2100`
- Enforce cross-reference consistency:
	- A product is inserted only if its `brand_name` exists in cleaned brands.
- Deduplicate records:
	- Brands: dedupe by `brand_name`
	- Products: dedupe by (`name`, `brand_name`)

Import behavior:
- Create collections if they do not exist.
- Insert seed data only when collection count is `0`.
- Optional full reset when `RESET_COLLECTIONS=true`.

## 5. Query Agent Behavior
The Query Agent is initialized with:
- Both collections (`Products`, `Brands`)
- A system prompt that prioritizes factual, grounded responses and transparency when information is missing.

Supported interaction modes:
- Direct single-question ask mode.
- Search-preview mode (`assistant.search`) for object-level snapshot output.
- Follow-up interaction via conversation messages.
- Aggregation-like requests interpreted by agent reasoning.

## 6. Demonstrated Query Scenarios
The CLI demo covers five required prompt types:

1. Normal search:
	 - "Show affordable shoes under 80 dollars with short reason why they are good."
2. Multi-collection query:
	 - "Which products come from brands focused on outdoor performance and what are their prices?"
3. Follow-up prompt:
	 - "From these suggestions, keep only in-stock options and prefer vintage style."
4. Filtering/aggregation-like question:
	 - "What is the average price of in-stock shoes and which brand has the highest priced shoe?"
5. Free-form request:
	 - "I need something stylish for rainy city walks and maybe a backup for formal evenings."

## 7. End-to-End Runtime Flow
1. Load `.env` configuration and validate required keys.
2. Connect to Weaviate Cloud with API-key auth and inference headers.
3. Ensure schema for `Products` and `Brands`.
4. Import cleaned seed data if collections are empty.
5. Initialize Query Agent over both collections.
6. Execute user command or web action.
7. Return natural-language response (or transformation workflow status).

## 8. Environment and Configuration
Required environment variables:
- `WEAVIATE_URL`
- `WEAVIATE_API_KEY`
- `INFERENCE_PROVIDER_API_KEY`

Optional variables:
- `GOOGLE_STUDIO_API_KEY`
- `RESET_COLLECTIONS` (default: `false`)
- `FLASK_HOST` (default: `127.0.0.1`)
- `FLASK_PORT` (default: `5000`)

## 9. Strengths
- Clean separation of concerns (config, client, ingestion, assistant, UI).
- Reliable setup flow for demos and repeated execution.
- Multi-interface support (CLI and web) without duplicated core logic.
- Data cleaning and validation improves consistency and answer quality.

## 10. Limitations
- Answer quality depends on model behavior and dataset coverage.
- Aggregation-like responses are agent-generated, not strict SQL aggregates.
- Transformation Agent is preview-oriented and should be used on test data.
- No automated test suite yet.
- No persistent chat history or user profile memory yet.

## 11. Future Improvements
- Add unit and integration tests with mocked Weaviate client.
- Add persistent conversation history storage.
- Add evaluation metrics (latency, answer groundedness, relevance).
- Add schema migration/versioning strategy.
- Expand UI with structured filters and exportable answers.

## 12. Conclusion
The project successfully demonstrates an end-to-end AI retrieval workflow on e-commerce data using Weaviate Agents. It combines structured ingestion, multi-collection querying, and practical interfaces into a clear baseline for further academic or production-focused iteration.
