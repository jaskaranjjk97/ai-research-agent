from app.graph.state import ResearchGraphState
from app.models.evidence import Evidence
from app.models.research import ResearchQuestion
from app.models.source import Source
from app.services.source_service import SourceService
from app.tools.extraction import ExtractionTool


class EvidenceExtractor:
    """Extract evidence from a source for research questions."""

    def __init__(self, extraction_tool: ExtractionTool) -> None:
        self.extraction_tool = extraction_tool

    async def extract(
        self, source: Source, research_question: ResearchQuestion
    ) -> list[Evidence]:
        """Extract the evidences from source for research question."""

        return await self.extraction_tool.extract(
            source=source,
            question=research_question,
        )


async def extractor_node(
    state: ResearchGraphState,
    source_service: SourceService,
    evidence_extractor: EvidenceExtractor,
) -> ResearchGraphState:
    """extract evidence from source and update the research state."""

    research_state = state["research_state"]

    if not research_state.plan:
        raise ValueError("plan can not be empty.")

    if research_state.current_question_id is None:
        raise ValueError("Need current+question_id before running the extractor node")

    question = next(
        (
            item
            for item in research_state.plan.questions
            if item.id == research_state.current_question_id
        ),
        None,
    )

    if question is None:
        raise ValueError("Current research question could not be found in the plan.")

    relevant_results = [
        result
        for result in research_state.search_results
        if result.question_id == question.id
    ]

    for search_result in relevant_results:
        source = await source_service.fetch_source(search_result)

        research_state.sources.append(source)

        evidence = await evidence_extractor.extract(
            source=source,
            research_question=question,
        )

        research_state.evidences.extend(evidence)
    return state
