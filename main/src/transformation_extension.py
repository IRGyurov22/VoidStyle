from weaviate.agents.classes import Operations
from weaviate.agents.transformation import TransformationAgent
from weaviate.classes.config import DataType

from src.data_loader import PRODUCTS_COLLECTION


def run_transformation_demo(client):
    add_tags = Operations.append_property(
        property_name="auto_tags",
        data_type=DataType.TEXT_ARRAY,
        view_properties=["name", "category", "description"],
        instruction=(
            "Generate up to 5 concise e-commerce tags for each product based on name, "
            "category and description."
        ),
    )

    agent = TransformationAgent(
        client=client,
        collection=PRODUCTS_COLLECTION,
        operations=[add_tags],
    )

    response = agent.update_all()
    status = agent.get_status(workflow_id=response.workflow_id)
    return response.workflow_id, status
