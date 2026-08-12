from __future__ import annotations

from hashlib import sha256
from typing import Any

from ai.planner_policy import planner_policy
from services.postgres_store import postgres_store
from services.qdrant_store import qdrant_store
from services.vector_store import vector_store


class LearningLoop:
    def process(
        self,
        *,
        question: str,
        plan: dict[str, Any],
        context: dict[str, Any],
        reasoning: dict[str, Any],
        critic: dict[str, Any],
        answer: str,
        hypothesis: dict[str, Any],
        agent: dict[str, Any],
        semantic_query: dict[str, Any],
    ) -> dict[str, Any]:
        decision = {
            "intent": plan.get("intent", "unknown"),
            "capabilities": plan.get("capabilities", []),
            "tools": plan.get("tools", []),
            "agent": agent.get("name"),
            "selected_hypothesis": hypothesis.get("selected_hypothesis"),
            "critic_approved": bool(critic.get("approved", False)),
            "confidence": float(critic.get("confidence", 0.0) or 0.0),
            "semantic_query": semantic_query,
            "validated_query": semantic_query,
            "plan": plan,
        }
        evidence = context.get("evidence", []) if isinstance(context.get("evidence", []), list) else []

        insight_summary = self._build_insight_summary(decision=decision, reasoning=reasoning, hypothesis=hypothesis)
        signature = self._signature(question, decision, insight_summary)

        reused = self._was_reused(question=question, history=context.get("history", []))
        knowledge_updated = self._update_knowledge_index(
            question=question,
            answer=answer,
            insight_summary=insight_summary,
            signature=signature,
            plan=plan,
            hypothesis=hypothesis,
        )

        outcome = {
            "result": answer,
            "answer_preview": answer[:400],
            "insight_summary": insight_summary,
            "hypothesis_confidence": hypothesis.get("confidence", 0.0),
        }

        postgres_store.save_learning_cycle(
            question=question,
            intent=decision["intent"],
            decision=decision,
            evidence=evidence,
            outcome=outcome,
            knowledge_updated=knowledge_updated,
            metadata={"reused": reused, "signature": signature, "feedback": None, "correction": None},
        )

        postgres_store.save_insight(
            signature=signature,
            kind="learning.cycle",
            summary=insight_summary,
            payload={
                "question": question,
                "decision": decision,
                "hypothesis": hypothesis,
                "reasoning": reasoning,
            },
        )

        planner_policy.feedback(
            capabilities=plan.get("capabilities", []),
            success=bool(critic.get("approved", False)),
            confidence=float(critic.get("confidence", 0.0) or 0.0),
        )

        return {
            "signature": signature,
            "knowledge_updated": knowledge_updated,
            "reused": reused,
            "insight_summary": insight_summary,
        }

    @staticmethod
    def _build_insight_summary(decision: dict[str, Any], reasoning: dict[str, Any], hypothesis: dict[str, Any]) -> str:
        intent = decision.get("intent", "unknown")
        agent = decision.get("agent", "SOFIA")
        selected = hypothesis.get("selected_hypothesis", "not-defined")
        recommended = reasoning.get("recommended_actions", [])
        action = recommended[0] if recommended else "collect more evidence"
        return (
            f"Intent {intent} handled by {agent}. "
            f"Primary hypothesis={selected}. "
            f"Recommended next action: {action}."
        )

    @staticmethod
    def _signature(question: str, decision: dict[str, Any], insight_summary: str) -> str:
        base = f"{question.lower().strip()}|{decision.get('intent')}|{decision.get('selected_hypothesis')}|{insight_summary}"
        return sha256(base.encode("utf-8")).hexdigest()

    @staticmethod
    def _was_reused(question: str, history: list[dict[str, Any]]) -> bool:
        if not isinstance(history, list) or not history:
            return False
        q_tokens = set(question.lower().split())
        if not q_tokens:
            return False

        for item in reversed(history):
            if item.get("role") != "user":
                continue
            text = str(item.get("text", "")).lower()
            if not text.strip():
                continue
            h_tokens = set(text.split())
            if not h_tokens:
                continue
            overlap = len(q_tokens.intersection(h_tokens)) / max(len(q_tokens), 1)
            if overlap >= 0.6:
                return True
        return False

    @staticmethod
    def _update_knowledge_index(
        *,
        question: str,
        answer: str,
        insight_summary: str,
        signature: str,
        plan: dict[str, Any],
        hypothesis: dict[str, Any],
    ) -> bool:
        payload = (
            f"question: {question}\n"
            f"answer: {answer}\n"
            f"insight: {insight_summary}\n"
            f"intent: {plan.get('intent')}\n"
            f"selected_hypothesis: {hypothesis.get('selected_hypothesis')}\n"
            f"signature: {signature}"
        )

        vector_store.add(
            payload,
            {
                "source": "learning_loop",
                "signature": signature,
                "intent": plan.get("intent", "unknown"),
            },
        )
        qdrant_ok = qdrant_store.add_text(
            payload,
            {
                "source": "learning_loop",
                "signature": signature,
                "intent": plan.get("intent", "unknown"),
            },
        )
        return bool(qdrant_ok)


learning_loop = LearningLoop()
