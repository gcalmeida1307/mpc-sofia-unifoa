"""Allowlisted tool contracts used by the HTTP and MCP adapters."""

from __future__ import annotations

from .contracts import ToolContract

TOOL_CONTRACTS = {
    "list_knowledge_modules": ToolContract("list_knowledge_modules", None, "Lista módulos e estado do conhecimento", "knowledge.catalog", 20.0, "tool_module_catalog"),
    "tensor_multiply": ToolContract("tensor_multiply", None, "Multiplicação matricial isolada", "numerical.tensor", 10.0, "tool_tensor"),
    "random_generate": ToolContract("random_generate", None, "Amostragem aleatória reprodutível", "numerical.random", 10.0, "tool_random"),
    "monte_carlo_estimate": ToolContract("monte_carlo_estimate", None, "Estimativa Monte Carlo", "numerical.monte_carlo", 20.0, "tool_monte_carlo"),
    "neural_train": ToolContract("neural_train", None, "Treinamento isolado por módulo", "neural.train", 300.0, "tool_neural_train"),
    "neural_status": ToolContract("neural_status", None, "Estado do modelo neural", "neural.read", 10.0, "tool_neural_status"),
    "neural_infer": ToolContract("neural_infer", None, "Inferência do modelo neural", "neural.infer", 20.0, "tool_neural_infer"),
    "neural_graph": ToolContract("neural_graph", None, "Grafo semântico observado", "neural.graph", 20.0, "tool_neural_graph"),
    "semantic_embedding_status": ToolContract("semantic_embedding_status", None, "Estado dos embeddings neurais locais", "knowledge.read", 20.0, "tool_embedding_status"),
    "semantic_embed": ToolContract("semantic_embed", None, "Construção sequencial de embeddings locais", "admin.training", 300.0, "tool_embedding_build"),
    "readiness_check": ToolContract("readiness_check", None, "Checklist operacional de escala do módulo", "admin.evaluation", 60.0, "tool_readiness_check"),
    "search_knowledge": ToolContract("search_knowledge", None, "Busca local no conhecimento autorizado", "knowledge.read", 30.0, "tool_search_knowledge"),
    "rag_answer": ToolContract("rag_answer", None, "Resposta com RAG e verificação", "knowledge.answer", 180.0, "tool_rag_answer"),
    "analyst_scenario": ToolContract("analyst_scenario", None, "Analista de cenários", "analysis.run", 180.0, "tool_analyst"),
    "agent_plan": ToolContract("agent_plan", None, "Plano de execução sem ação externa", "agent.plan", 20.0, "tool_agent_plan"),
    "agent_memory_status": ToolContract("agent_memory_status", None, "Métricas de memória operacional", "agent.memory.read", 20.0, "tool_agent_memory"),
    "query_theme_report": ToolContract("query_theme_report", None, "Estatística administrativa de temas", "admin.statistics", 20.0, "tool_theme_report"),
    "institutional_integration_status": ToolContract("institutional_integration_status", None, "Status de conectores institucionais", "admin.integrations", 20.0, "tool_integrations"),
    "institutional_integration_sync": ToolContract("institutional_integration_sync", None, "Sincronização paginada aprovada", "admin.integrations", 300.0, "tool_integrations"),
}


def contracts() -> list[dict[str, object]]:
    return [item.__dict__ for item in TOOL_CONTRACTS.values()]
