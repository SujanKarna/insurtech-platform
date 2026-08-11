from dataclasses import dataclass

from config.settings import (
    GDV_AUB_EMBEDDINGS_PATH,
    EMBEDDING_MODEL_NAME,
)

from embedding.embedder import BGEEmbedder
from retrieval.semantic_search import SemanticSearcher


# ============================================================================
# Evaluation case
# ============================================================================

@dataclass
class EvaluationCase:
    """
    A single retrieval evaluation query.

    expected_sections contains section numbers that are considered
    acceptable answers for the query.
    """

    query: str
    expected_sections: list[str]


# ============================================================================
# Test dataset
# ============================================================================

EVALUATION_CASES = [

    EvaluationCase(
        query="Was ist ein Unfall?",
        expected_sections=["1.3"],
    ),

    EvaluationCase(
        query="Was passiert bei Vorinvalidität?",
        expected_sections=["2.1.2.2.3"],
    ),

    EvaluationCase(
        query="Wie wird der Invaliditätsgrad berechnet?",
        expected_sections=[
            "2.1.2.1",
            "2.1.2.2",
        ],
    ),

    EvaluationCase(
        query="Wann besteht Anspruch auf Invaliditätsleistung?",
        expected_sections=[
            "2.1",
            "2.1.1",
        ],
    ),

    EvaluationCase(
        query="Was passiert bei Krankheiten oder Gebrechen?",
        expected_sections=[
            "3",
            "3.1",
            "3.2",
        ],
    ),

    EvaluationCase(
        query="Wann wird eine Unfallrente gezahlt?",
        expected_sections=[
            "2.2",
            "2.2.1",
            "2.2.2",
            "2.2.3",
        ],
    ),

    EvaluationCase(
        query="Was gilt bei einem Unfall unter Wasser?",
        expected_sections=["1.4.3"],
    ),

    EvaluationCase(
        query="Welche Unfälle sind nicht versichert?",
        expected_sections=[
            "5",
            "5.1",
        ],
    ),

    EvaluationCase(
        query="Welche Kosten für Such- und Rettungseinsätze werden übernommen?",
        expected_sections=[
            "2.8",
            "2.8.1",
            "2.8.2",
        ],
    ),

    EvaluationCase(
        query="Wie lange muss die Invalidität bestehen?",
        expected_sections=[
            "2.1.1.1",
            "2.1.1.2",
        ],
    ),
]


# ============================================================================
# Evaluation helpers
# ============================================================================

def is_relevant(
    result: dict,
    expected_sections: list[str],
) -> bool:
    """
    Determine whether a retrieved result is relevant.

    A result is considered relevant when its section number matches
    one of the expected section numbers.
    """

    section_number = result[
        "section_number"
    ]

    return section_number in expected_sections


def reciprocal_rank(
    results: list[dict],
    expected_sections: list[str],
) -> float:
    """
    Calculate Reciprocal Rank.

    If the first relevant result is at position:

        1 -> 1.0
        2 -> 0.5
        3 -> 0.333
        ...

    Returns 0 if no relevant result is found.
    """

    for rank, result in enumerate(
        results,
        start=1,
    ):

        if is_relevant(
            result,
            expected_sections,
        ):
            return 1.0 / rank

    return 0.0


# ============================================================================
# Main evaluation
# ============================================================================

def main() -> None:

    print(
        "Starting retrieval evaluation..."
    )

    print()

    # ------------------------------------------------------------------------
    # Load model
    # ------------------------------------------------------------------------

    embedder = BGEEmbedder(
        model_name=EMBEDDING_MODEL_NAME,
    )

    # ------------------------------------------------------------------------
    # Load embedded chunks
    # ------------------------------------------------------------------------

    searcher = SemanticSearcher(
        embeddings_path=GDV_AUB_EMBEDDINGS_PATH,
        embedder=embedder,
    )

    print()

    # ------------------------------------------------------------------------
    # Evaluation counters
    # ------------------------------------------------------------------------

    hit_at_1 = 0
    hit_at_3 = 0
    hit_at_5 = 0

    reciprocal_ranks = []

    # ------------------------------------------------------------------------
    # Evaluate every query
    # ------------------------------------------------------------------------

    for index, case in enumerate(
        EVALUATION_CASES,
        start=1,
    ):

        results = searcher.search(
            query=case.query,
            top_k=5,
        )

        # ---------------------------------------------------------------
        # Check Hit@1
        # ---------------------------------------------------------------

        hit1 = (
            len(results) >= 1
            and is_relevant(
                results[0],
                case.expected_sections,
            )
        )

        # ---------------------------------------------------------------
        # Check Hit@3
        # ---------------------------------------------------------------

        hit3 = any(
            is_relevant(
                result,
                case.expected_sections,
            )
            for result in results[:3]
        )

        # ---------------------------------------------------------------
        # Check Hit@5
        # ---------------------------------------------------------------

        hit5 = any(
            is_relevant(
                result,
                case.expected_sections,
            )
            for result in results[:5]
        )

        # ---------------------------------------------------------------
        # Update metrics
        # ---------------------------------------------------------------

        if hit1:
            hit_at_1 += 1

        if hit3:
            hit_at_3 += 1

        if hit5:
            hit_at_5 += 1

        rr = reciprocal_rank(
            results,
            case.expected_sections,
        )

        reciprocal_ranks.append(rr)

        # ---------------------------------------------------------------
        # Print result
        # ---------------------------------------------------------------

        print(
            f"[{index:02d}] {case.query}"
        )

        print(
            f"     Expected : "
            f"{', '.join(case.expected_sections)}"
        )

        print(
            f"     Top      : "
            f"{results[0]['section_number']} "
            f"{results[0]['section_title']}"
        )

        print(
            f"     Score    : "
            f"{results[0]['score']:.4f}"
        )

        print(
            f"     Hit@1    : "
            f"{'YES' if hit1 else 'NO'}"
        )

        print(
            f"     Hit@3    : "
            f"{'YES' if hit3 else 'NO'}"
        )

        print(
            f"     Hit@5    : "
            f"{'YES' if hit5 else 'NO'}"
        )

        print(
            f"     RR       : "
            f"{rr:.4f}"
        )

        print()

    # =========================================================================
    # Final metrics
    # =========================================================================

    total = len(
        EVALUATION_CASES
    )

    hit_at_1_score = (
        hit_at_1 / total
    )

    hit_at_3_score = (
        hit_at_3 / total
    )

    hit_at_5_score = (
        hit_at_5 / total
    )

    mrr = (
        sum(reciprocal_ranks)
        / total
    )

    # ------------------------------------------------------------------------
    # Print summary
    # ------------------------------------------------------------------------

    print("=" * 80)
    print("RETRIEVAL EVALUATION")
    print("=" * 80)

    print(
        f"Queries : {total}"
    )

    print()

    print(
        f"Hit@1   : "
        f"{hit_at_1}/{total} "
        f"({hit_at_1_score:.2%})"
    )

    print(
        f"Hit@3   : "
        f"{hit_at_3}/{total} "
        f"({hit_at_3_score:.2%})"
    )

    print(
        f"Hit@5   : "
        f"{hit_at_5}/{total} "
        f"({hit_at_5_score:.2%})"
    )

    print(
        f"MRR     : "
        f"{mrr:.4f}"
    )

    print("=" * 80)


if __name__ == "__main__":
    main()