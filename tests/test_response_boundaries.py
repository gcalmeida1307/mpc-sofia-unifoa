from api.policies import policy_for
from api.response_policy import choose_response_policy, should_enqueue_unanswered_topic
from api.retrieval import RetrievalResult
from api.session_context import MAX_HISTORY_CHARS, bound_history


def test_chat_history_is_bounded_before_it_reaches_the_core() -> None:
    history = [
        {"role": "user", "content": f"pergunta {index} " + ("x" * 2400)}
        for index in range(20)
    ]

    bounded = bound_history(history)

    assert len(bounded) <= 6
    assert sum(len(item["content"]) for item in bounded) <= MAX_HISTORY_CHARS
    assert all(len(item["content"]) <= 1600 for item in bounded)
    assert bounded[-1]["content"].startswith("pergunta 19")


def test_greetings_and_successful_answers_never_enter_expansion_queue() -> None:
    assert not should_enqueue_unanswered_topic(
        evidence_found=False,
        context_package={"retrieval_required": False, "task_route": "conversation"},
    )
    assert not should_enqueue_unanswered_topic(
        evidence_found=True,
        context_package={"retrieval_required": True, "task_route": "document_rag"},
    )


def test_only_an_unanswered_documentary_task_enters_expansion_queue() -> None:
    assert should_enqueue_unanswered_topic(
        evidence_found=False,
        context_package={"retrieval_required": True, "task_route": "document_rag"},
    )
    assert not should_enqueue_unanswered_topic(
        evidence_found=False,
        context_package={"retrieval_required": True, "task_route": "conversation"},
    )


def test_evidence_is_the_only_authority_for_the_generation_boundary() -> None:
    empty = RetrievalResult((), (), "pergunta", "pergunta")
    plan = type("Plan", (), {"strategy": "FACT_LOOKUP"})()

    grounded = choose_response_policy(
        empty,
        query_plan=plan,
        policy=policy_for("direito"),
        provider="auto",
        external_allowed=False,
    )
    assert grounded.route == "external_assist"
    assert grounded.use_local_evidence is False

    clinical = choose_response_policy(
        empty,
        query_plan=plan,
        policy=policy_for("medicina"),
        provider="auto",
        external_allowed=True,
    )
    assert clinical.route == "evidence_gap"
    assert clinical.allow_external_assist is False
