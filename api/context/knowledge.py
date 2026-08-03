from __future__ import annotations

from services.knowledge import search_knowledge


class KnowledgeProvider:
    def execute(self, tool_name: str, question: str) -> dict:
        if tool_name != "knowledge.search":
            return {"error": f"unsupported knowledge tool: {tool_name}"}
        return search_knowledge(question)


knowledge_provider = KnowledgeProvider()