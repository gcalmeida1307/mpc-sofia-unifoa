# Gateway semântico da SOFIA

O gateway separa linguagem natural de execução operacional. Nenhum texto produzido por Claude ou Ollama é usado diretamente como nome de grupo, ferramenta, SQL ou comando.

```text
Pergunta -> SemanticGateway -> SemanticQuery JSON -> Pydantic/allowlists
         -> Planner -> agente por domínio -> executor autorizado -> resposta -> aprendizado
```

Se o provedor estiver indisponível, devolver JSON inválido ou adicionar campos desconhecidos, a resposta é descartada. O interpretador determinístico assume a classificação e nunca executa o texto inválido.

## Contrato canônico

`SemanticQuery` registra intenção, domínio, fonte autorizada, entidade canônica, período de 1 a 90 dias, métrica, estado, agrupamento, ambiguidades, confiança e origem da interpretação.

Entidades Zabbix são convertidas por allowlist. Por exemplo, variações de `switch` resultam no grupo exato `Switches`. Nomes livres não seguem para a API do Zabbix.

## Responsabilidades

- `api/semantic/`: interpretação, fallback, validação, exemplos e execução semântica.
- `api/ai/planner.py`: transforma o contrato validado em capacidades e ferramentas.
- `api/ai/agent_runtime.py`: seleciona o agente pelo domínio/intenção normalizados.
- `api/zabbix/`: filtros e agregações; hosts são deduplicados por `hostid`.
- `api/presentation/`: formatação, sem decidir o escopo.
- `api/ai/operational_query.py`: compatibilidade legada; não é a porta principal do planner.
- `api/ai/learning_loop.py`: persiste pergunta, consulta semântica, consulta validada, plano, resultado, feedback e correção.

## Como ampliar

1. Adicione o valor ao modelo em `api/semantic/models.py`.
2. Inclua somente valores executáveis na allowlist.
3. Adicione exemplos representativos.
4. Mapeie a intenção para capacidades no planner.
5. Implemente o executor sem usar texto livre como parâmetro sensível.
6. Inclua paráfrases no teste de equivalência.

## Validação

```bash
docker compose up -d --build sofia-api
docker compose exec -T sofia-api pytest -q
curl -fsS http://localhost:8080/health
curl -fsS http://localhost:8080/mcp/health
```

O teste central está em `api/tests/test_semantic_gateway.py`: perguntas equivalentes devem produzir a mesma assinatura lógica e o mesmo plano.
