import pytest
from pydantic import ValidationError

from app.models.research import (
    ResearchDepth,
    ResearchPlan,
    ResearchQuestion,
    ResearchQuestionStatus,
    ResearchRequest,
)


def test_research_request_defaults_to_standard_depth():
    request = ResearchRequest(query="Research the Indian electric vehicle market.")

    assert request.depth == ResearchDepth.STANDARD


def test_research_request_accepts_deep_research():
    request = ResearchRequest(
        query="Research the Indian electric vehicle market.",
        depth=ResearchDepth.DEEP,
    )

    assert request.depth == ResearchDepth.DEEP


def test_research_request_rejects_short_query():
    with pytest.raises(ValidationError):
        ResearchRequest(query="Hi")


def test_research_request_rejects_empty_query():
    with pytest.raises(ValidationError):
        ResearchRequest(query="")


def test_research_request_rejects_excessively_long_query():
    with pytest.raises(ValidationError):
        ResearchRequest(query="a" * 5001)


def test_research_question_defaults_to_pending():
    question = ResearchQuestion(
        id="q1",
        question="What is the current EV market size?",
    )

    assert question.status == ResearchQuestionStatus.PENDING
    assert question.priority == 1


def test_research_question_accepts_priority():
    question = ResearchQuestion(
        id="q1",
        question="What is the current EV market size?",
        priority=5,
    )

    assert question.priority == 5


def test_research_question_rejects_invalid_priority():
    with pytest.raises(ValidationError):
        ResearchQuestion(
            id="q1",
            question="What is the current EV market size?",
            priority=6,
        )


def test_research_plan_contains_questions():
    question = ResearchQuestion(
        id="q1",
        question="What is the current EV market size?",
        priority=5,
    )

    plan = ResearchPlan(
        objective="Understand the Indian EV market.",
        questions=[question],
    )

    assert plan.objective == "Understand the Indian EV market."
    assert len(plan.questions) == 1
    assert plan.questions[0].id == "q1"


def test_research_plan_requires_at_least_one_question():
    with pytest.raises(ValidationError):
        ResearchPlan(
            objective="Understand the Indian EV market.",
            questions=[],
        )
