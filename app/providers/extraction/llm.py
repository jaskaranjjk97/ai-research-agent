import json

from app.models.evidence import Evidence
from app.models.research import ResearchQuestion
from app.models.source import Source
from app.providers.extraction.base import ExtractionProvider
from app.providers.llm.base import LLMProvider


class LLMExtractionProvider(ExtractionProvider):
    """abstrct implementation of extraction provider."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        self.llm_provider = llm_provider

    async def extract(
        self, source: Source, question: ResearchQuestion
    ) -> list[Evidence]:
        """Extract the evidences from source with help of llm."""

        prompt = self._build_prompt(source, question)
        response = await self.llm_provider.generate(prompt)

        items = json.loads(response)

        if not isinstance(items, list):
            raise ValueError("Extraction response must be a JSON array.")

        evidences: list[Evidence] = []

        for item in items:
            evidence = Evidence(
                evidence_id=item["evidence_id"],
                source_id=source.source_id,
                question_id=question.id,
                content=item["content"],
                location=item.get("location"),
            )

            evidences.append(evidence)

        return evidences

    @staticmethod
    def _build_prompt(source: Source, question: ResearchQuestion) -> str:

        return f"""
        Extract Evidence relevant to research question from the source below.

Research Question:
{question.question}

Source ID:
{source.source_id}

Source title:
{source.title}

Source content:
{source.content}

Return only a valid JSON array. Each item must contain:
- evidence_id: a unique string
- content: an exact passage or faithful excerpt from the source
- location: a section heading or other location, if available

Rules:
1. Extract only evidence relevant to the research question.
2. Do not invent facts or use information outside the source.
3. If no relevant evidence exists, return an empty array.
4. Preserve the meaning of the source.
5. Return JSON only, without Markdown fences.
""".strip()
