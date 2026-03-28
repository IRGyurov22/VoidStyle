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
    brands = _read_json(data_dir / "brands.json")
    products = _read_json(data_dir / "products.json")

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
