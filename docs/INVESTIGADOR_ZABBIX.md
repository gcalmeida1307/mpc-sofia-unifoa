# Investigador profundo do Zabbix

## Fluxo

```text
pergunta validada
→ problemas relacionados
→ triggers e funções
→ itens de origem e itens do mesmo componente
→ valor atual/anterior
→ histórico de 1 a 24 horas
→ host, interfaces, inventário e templates
→ dependências e recorrência de 1 a 30 dias
→ relatório factual
```

O executor é somente leitura. Claude pode interpretar a intenção da pergunta, mas o relatório operacional é montado a partir do contrato de evidências; causa, equipamento conectado e traduções de valores não são inventados.

## API

`POST /zabbix/investigate`, disponível apenas para administradores:

```json
{
  "question": "Investigue enlace indisponível no Fortigate-600E",
  "hours": 2,
  "recurrence_days": 7,
  "max_problems": 20
}
```

Limites: 50 problemas, 150 itens de origem, histórico máximo de 24 horas e recorrência máxima de 30 dias.

## Cobertura

O investigador funciona para qualquer template que exponha triggers e itens:

- rede: estado, velocidade, duplex, tráfego, erros e descartes por interface;
- sistema operacional: CPU, fila, memória, swap, disco, filesystem, processos e serviços;
- banco, storage, firewall e demais tecnologias: itens vinculados à trigger e histórico disponível.

O contrato informa explicitamente lacunas. Para descobrir o equipamento conectado, o template precisa coletar LLDP/CDP. Para diferenciar porta desabilitada de falha operacional, precisa coletar `ifAdminStatus`. Logs precisam existir como item Zabbix ou ser consultados por Loki/Syslog/API.

## Interface

Ao abrir um risco na Executive View, o botão **Investigar evidências no Zabbix** preenche o chat com uma solicitação explícita. O planner seleciona `zabbix.investigate`, e o relatório retorna portas ou componentes, valores, horários, histórico, recorrência e dados não comprovados.
