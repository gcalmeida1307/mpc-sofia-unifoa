# Executive View

## Princípio

Uma tela, cinco segundos, uma decisão. A tela executiva não exibe logs, prompts, nomes internos de modelos ou evidências brutas. O detalhamento permanece na Analyst View (`/ui/analista.html`).

## Contrato

`GET /dashboard/executive` devolve um contrato somente de leitura com:

- saúde geral, tendência e comparação com o dia anterior;
- total estático de dispositivos e mudança real desde a hora anterior;
- saúde por área;
- até cinco riscos traduzidos;
- alertas novos, equipamentos novos, problemas resolvidos e incidentes críticos;
- ação prioritária e histórico horário de saúde.

## Regras auditáveis

Versão atual: `executive-health-v1`.

1. A saúde é calculada localmente a partir das severidades Zabbix. Claude não calcula nem altera valores.
2. Pesos: não classificado `0,1`, informação `0,25`, aviso `0,75`, médio `1,5`, alto `3` e desastre `5`.
3. Pontuação: `100 - (soma dos pesos / dispositivos monitorados) × 4`, limitada entre 0 e 100.
4. Áreas são classificadas por grupos e famílias conhecidas: Rede, Servidores, Telefonia, Storage e Segurança.
5. Equipamento novo é exclusivamente a diferença positiva da contagem de hosts entre snapshots. Sem regra de descoberta ou alteração da contagem, o valor permanece zero.
6. Alertas novos e resolvidos são diferenças entre `eventid` atuais e os do snapshot de referência de uma hora.
7. Incidente crítico é um problema ativo com severidade alta ou desastre.
8. Riscos são agrupados por regras locais traduzidas. Cada cartão expõe somente risco, impacto, confiança e próxima ação.

Ao selecionar um risco, a interface consulta os detalhes já presentes no mesmo contrato: explicação, ocorrências, equipamentos, áreas, severidades e três passos de tratamento. Essa abertura progressiva mantém a leitura executiva curta sem esconder o caminho de investigação.

Na Analyst View, o total de dispositivos aparece uma única vez. A linha horária representa somente variações de alertas. Cada ponto informa quantos alertas entraram, quantos foram resolvidos e apresenta até cinco descrições de cada lado; assim, uma variação não é exibida sem contexto.

Alterações nos pesos ou classificadores exigem nova versão de `ruleset` e testes de regressão.
