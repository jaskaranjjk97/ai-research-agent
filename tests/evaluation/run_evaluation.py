import json
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.models.claim import Claim
from app.models.report import ResearchReport
from app.models.source import Source
from tests.evaluation.scoring import EvaluationScore, evaluate_report

DATASET_PATH = Path(__file__).parent / "datasets" / "research_cases.json"


def load_dataset(path: Path) -> dict[str, Any]:
    """Load the evaluation dataset from JSON."""
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def evaluate_case(case: dict[str, Any]) -> EvaluationScore:
    """Validate and evaluate one dataset case."""
    claims = [Claim.model_validate(item) for item in case["claims"]]
    sources = [Source.model_validate(item) for item in case["sources"]]
    report = ResearchReport.model_validate(case["report"])

    return evaluate_report(
        report=report,
        claims=claims,
        sources=sources,
        expected_sections=case["expected_sections"],
    )


def main() -> int:
    """Run the evaluation dataset and print scores."""
    try:
        dataset = load_dataset(DATASET_PATH)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Unable to load evaluation dataset: {exc}", file=sys.stderr)
        return 1

    cases = dataset.get("cases", [])

    if not cases:
        print("Evaluation dataset contains no cases.", file=sys.stderr)
        return 1

    results: list[tuple[str, EvaluationScore]] = []
    failures = 0

    print(f"Dataset: {dataset.get('dataset_name', 'unnamed')}")
    print(f"Version: {dataset.get('version', 'unknown')}")
    print(f"Cases: {len(cases)}")
    print("-" * 72)

    for case in cases:
        case_id = case.get("case_id", "unknown")

        try:
            score = evaluate_case(case)
        except (ValidationError, ValueError, KeyError, TypeError) as exc:
            failures += 1
            print(f"FAIL  {case_id}: {exc}")
            continue

        results.append((case_id, score))
        coverage = score.claim_citation_coverage

        coverage_text = "N/A" if coverage is None else f"{coverage:.1%}"

        print(
            f"PASS  {case_id} | "
            f"citation integrity={score.citation_integrity:.1%} | "
            f"claim citation coverage={coverage_text} | "
            f"section coverage={score.section_coverage:.1%}"
        )

    print("-" * 72)

    if results:
        print(f"Successfully evaluated: {len(results)}/{len(cases)}")

        average_citation_integrity = sum(
            score.citation_integrity for _, score in results
        ) / len(results)

        print(f"Average citation integrity: {average_citation_integrity:.1%}")

        coverage_scores = [
            score.claim_citation_coverage
            for _, score in results
            if score.claim_citation_coverage is not None
        ]

        if coverage_scores:
            average_claim_coverage = sum(coverage_scores) / len(coverage_scores)
            print(f"Average claim citation coverage: {average_claim_coverage:.1%}")
        else:
            print("Average claim citation coverage: N/A")

        average_section_coverage = sum(
            score.section_coverage for _, score in results
        ) / len(results)

        print(f"Average section coverage: {average_section_coverage:.1%}")

    print(f"Failed cases: {failures}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
