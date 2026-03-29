import json
from pathlib import Path
from typing import Any

from weaviate.classes.config import Configure, DataType, Property


BRANDS_COLLECTION = "Brands"
PRODUCTS_COLLECTION = "Products"


class DataLoaderError(Exception):
    pass


def _read_json(path: Path) -> list[dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise DataLoaderError(f"Failed reading JSON file: {path}") from exc


def _normalize_text(value: Any) -> str:
    return " ".join(str(value).strip().split())


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "in stock", "instock"}:
            return True
        if normalized in {"false", "0", "no", "n", "out of stock", "oos"}:
            return False

    return bool(value)


def _dedupe_rows(rows: list[dict[str, Any]], key_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    seen: set[tuple[str, ...]] = set()
    deduped: list[dict[str, Any]] = []

    for row in rows:
        key = tuple(_normalize_text(row.get(field, "")).lower() for field in key_fields)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    return deduped


def _clean_brands(raw_brands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []

    for row in raw_brands:
        brand_name = _normalize_text(row.get("brand_name", ""))
        country = _normalize_text(row.get("country", ""))
        style_focus = _normalize_text(row.get("style_focus", "")).lower()
        brand_story = _normalize_text(row.get("brand_story", ""))

        if not (brand_name and country and style_focus and brand_story):
            continue

        try:
            founded_year = int(row.get("founded_year"))
        except (TypeError, ValueError):
            continue

        if founded_year < 1800 or founded_year > 2100:
            continue

        cleaned.append(
            {
                "brand_name": brand_name,
                "country": country,
                "founded_year": founded_year,
                "style_focus": style_focus,
                "brand_story": brand_story,
            }
        )

    return _dedupe_rows(cleaned, ("brand_name",))


def _clean_products(raw_products: list[dict[str, Any]], valid_brands: set[str]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []

    for row in raw_products:
        name = _normalize_text(row.get("name", ""))
        category = _normalize_text(row.get("category", "")).lower()
        brand_name = _normalize_text(row.get("brand_name", ""))
        description = _normalize_text(row.get("description", ""))

        if not (name and category and brand_name and description):
            continue

        if brand_name not in valid_brands:
            continue

        try:
            price = round(float(row.get("price")), 2)
        except (TypeError, ValueError):
            continue

        if price < 0:
            continue

        in_stock = _to_bool(row.get("in_stock", False))

        cleaned.append(
            {
                "name": name,
                "category": category,
                "price": price,
                "in_stock": in_stock,
                "brand_name": brand_name,
                "description": description,
            }
        )

    return _dedupe_rows(cleaned, ("name", "brand_name"))


def _create_brands_collection(client) -> None:
    if client.collections.exists(BRANDS_COLLECTION):
        return

    client.collections.create(
        name=BRANDS_COLLECTION,
        description="Brand metadata for e-commerce assistant.",
        vector_config=Configure.Vectors.text2vec_google_gemini(),
        properties=[
            Property(
                name="brand_name",
                data_type=DataType.TEXT,
                description="Public name of the brand.",
            ),
            Property(
                name="country",
                data_type=DataType.TEXT,
                description="Brand origin country.",
            ),
            Property(
                name="founded_year",
                data_type=DataType.INT,
                description="Year the brand was founded.",
            ),
            Property(
                name="style_focus",
                data_type=DataType.TEXT,
                description="Primary style or product direction.",
            ),
            Property(
                name="brand_story",
                data_type=DataType.TEXT,
                description="Short textual description of the brand.",
            ),
        ],
    )


def _create_products_collection(client) -> None:
    if client.collections.exists(PRODUCTS_COLLECTION):
        return

    client.collections.create(
        name=PRODUCTS_COLLECTION,
        description="Product catalog for e-commerce assistant.",
        vector_config=Configure.Vectors.text2vec_google_gemini(),
        properties=[
            Property(name="name", data_type=DataType.TEXT, description="Product name."),
            Property(
                name="category",
                data_type=DataType.TEXT,
                description="Product category.",
            ),
            Property(name="price", data_type=DataType.NUMBER, description="Product price."),
            Property(
                name="in_stock",
                data_type=DataType.BOOL,
                description="Whether product is currently available.",
            ),
            Property(
                name="brand_name",
                data_type=DataType.TEXT,
                description="Brand this product belongs to.",
            ),
            Property(
                name="description",
                data_type=DataType.TEXT,
                description="Text description used for semantic retrieval.",
            ),
        ],
    )


def reset_collections(client) -> None:
    for name in [PRODUCTS_COLLECTION, BRANDS_COLLECTION]:
        if client.collections.exists(name):
            client.collections.delete(name)


def ensure_schema(client) -> None:
    _create_brands_collection(client)
    _create_products_collection(client)


def import_seed_data(client, data_dir: Path) -> None:
    raw_brands = _read_json(data_dir / "brands.json")
    brands = _clean_brands(raw_brands)
    valid_brand_names = {row["brand_name"] for row in brands}

    raw_products = _read_json(data_dir / "products.json")
    products = _clean_products(raw_products, valid_brands=valid_brand_names)

    brands_collection = client.collections.get(BRANDS_COLLECTION)
    products_collection = client.collections.get(PRODUCTS_COLLECTION)

    if brands_collection.aggregate.over_all(total_count=True).total_count == 0:
        with brands_collection.batch.dynamic() as batch:
            for row in brands:
                batch.add_object(properties=row)

    if products_collection.aggregate.over_all(total_count=True).total_count == 0:
        with products_collection.batch.dynamic() as batch:
            for row in products:
                batch.add_object(properties=row)
