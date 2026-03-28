# Project Report (2-4 pages)

## 1. Goal
The goal is to build an intelligent app that uses Weaviate Query Agent to answer natural-language questions over e-commerce data stored in Weaviate Cloud.

## 2. Architecture
- Data layer: Weaviate Cloud with 2 collections (`Products`, `Brands`)
- Agent layer: Query Agent for NL querying, optional Transformation Agent for data enrichment
- Interface layer: Python CLI (`setup`, `demo`, `ask`, `transform`)

## 3. Used agents
### Query Agent
- Accepts natural-language questions
- Works over multiple collections
- Supports follow-up context and complex requests

### Transformation Agent (optional)
- Appends `auto_tags` to product objects
- Runs asynchronously
- Returns `workflow_id` and status via polling

## 4. Data model and ingestion
### Products
- name, category, price, in_stock, brand_name, description

### Brands
- brand_name, country, founded_year, style_focus, brand_story

Ingestion is performed from JSON files in `data/`.

## 5. Example inputs/outputs
1. Normal search: "Show affordable shoes under 80 dollars..."
2. Multi-collection: "Which products come from brands focused on outdoor performance..."
3. Follow-up: context-aware refinement after previous answer
4. Filtering/aggregation-like: average price and max-priced brand
5. Free-form prompt: broad style and use-case intent

## 6. Processing logic
- Validate environment and connect to Weaviate Cloud
- Ensure schema for both collections
- Import seed objects if collections are empty
- Initialize Query Agent with both collections and system prompt
- Execute prompts and return final answers

## 7. Limitations
- Results depend on model quality and collection coverage
- Aggregation-like reasoning is delegated to Query Agent behavior
- Transformation Agent is technical preview and should be used on test data

## 8. Future improvements
- Add a lightweight web UI (Streamlit)
- Add persistent conversation history storage
- Add Personalization Agent module for user profiles and interactions
- Add automated tests with mocked client for CI stability
