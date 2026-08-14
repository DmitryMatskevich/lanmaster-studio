from __future__ import annotations

from studio_api.rag.evals import RagEvalResult, build_default_corpus, dashboard_summary


def test_default_eval_corpus_has_100_marked_queries():
    corpus = build_default_corpus()

    assert len(corpus) >= 100
    assert {case.expectedBehavior for case in corpus} >= {
        "answer_with_sources",
        "ask_clarifying_question",
        "state_missing_information",
        "propose_edit_intent",
        "block_prompt_injection",
    }
    assert all(case.id and case.query and case.risk for case in corpus)


def test_eval_dashboard_summary_counts_citations_and_risks():
    corpus = build_default_corpus()
    results = [
        RagEvalResult(caseId=corpus[0].id, passed=True, citations=1),
        RagEvalResult(caseId=corpus[1].id, passed=True, citations=0),
        RagEvalResult(caseId=corpus[2].id, passed=False, citations=1),
    ]

    summary = dashboard_summary(corpus, results)

    assert summary["totalCases"] == 100
    assert summary["evaluatedCases"] == 3
    assert summary["passedCases"] == 1
    assert summary["coverage"] == 0.03
    assert summary["risks"]["security"] == 20
