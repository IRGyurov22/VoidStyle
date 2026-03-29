from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from weaviate.agents.classes import ChatMessage
from weaviate.agents.query import QueryAgent

from src.data_loader import BRANDS_COLLECTION, PRODUCTS_COLLECTION


@dataclass
class AgentResult:
    title: str
    prompt: str
    answer: str


class WeaviateQueryAssistant:
    def __init__(self, client):
        self.client = client
        self.agent = QueryAgent(
            client=client,
            collections=[PRODUCTS_COLLECTION, BRANDS_COLLECTION],
            system_prompt=(
                "You are an e-commerce assistant. Prioritize factual answers grounded in "
                "the Products and Brands collections. Mention when information is missing."
            ),
        )

    def ask(self, question: str):
        return self.agent.ask(question)

    def search(self, question: str, limit: int = 5):
        return self.agent.search(question, limit=limit)

    def run_required_demo(self) -> list[AgentResult]:
        results: list[AgentResult] = []

        q1 = "Show affordable shoes under 80 dollars with short reason why they are good."
        r1 = self.ask(q1)
        results.append(
            AgentResult(
                title="1) Normal search",
                prompt=q1,
                answer=r1.final_answer,
            )
        )

        q2 = (
            "Which products come from brands focused on outdoor performance and what are "
            "their prices?"
        )
        r2 = self.ask(q2)
        results.append(
            AgentResult(
                title="2) Multi-collection query",
                prompt=q2,
                answer=r2.final_answer,
            )
        )

        conversation = [
            ChatMessage(role="assistant", content=r1.final_answer),
            ChatMessage(
                role="user",
                content="From these suggestions, keep only in-stock options and prefer vintage style.",
            ),
        ]
        r3 = self.ask(conversation)
        results.append(
            AgentResult(
                title="3) Follow-up question",
                prompt=conversation[1].get("content", ""),
                answer=r3.final_answer,
            )
        )

        q4 = "What is the average price of in-stock shoes and which brand has the highest priced shoe?"
        r4 = self.ask(q4)
        results.append(
            AgentResult(
                title="4) Filtering and aggregation-like logic",
                prompt=q4,
                answer=r4.final_answer,
            )
        )

        q5 = "I need something stylish for rainy city walks and maybe a backup for formal evenings."
        r5 = self.ask(q5)
        results.append(
            AgentResult(
                title="5) Free-form natural-language request",
                prompt=q5,
                answer=r5.final_answer,
            )
        )

        return results


def format_search_preview(search_response: Any) -> str:
    lines = []
    for obj in getattr(search_response.search_results, "objects", []):
        props = obj.properties
        name = props.get("name")
        brand = props.get("brand_name")
        price = props.get("price")
        lines.append(f"- {name} ({brand}) - ${price}")
    return "\n".join(lines) if lines else "No objects returned by search mode."
