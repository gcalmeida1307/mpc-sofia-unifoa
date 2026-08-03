from __future__ import annotations

from learning.service import learning_service


class LearningProvider:
    def execute(self, tool_name: str, question: str) -> dict:
        if tool_name != "learning.insights":
            return {"error": f"unsupported learning tool: {tool_name}"}
        return learning_service.learn(question)


learning_provider = LearningProvider()
