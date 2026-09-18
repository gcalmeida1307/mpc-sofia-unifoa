# Interoperabilidade — escopo controlado

## FHIR

O SOFIA mantém um adaptador local FHIR R4 (`4.0.1`) isolado no módulo de
interoperabilidade. As rotas `/fhir/R4/*` e as rotas legadas `/fhir/*` apontam
para o mesmo armazenamento e passam pelas permissões do módulo Medicina.

O adaptador não declara conformidade hospitalar por si só. Validação de perfis,
terminologias, consentimento, auditoria e integração com um HIS continuam
dependendo do ambiente que receberá a solução.

## HL7 v2 e TISS

HL7 v2 e TISS ficam deliberadamente fora do núcleo genérico até existir um
contrato de integração. Para cada cliente, registrar antes da implementação:

- mensagens/transações necessárias e versões;
- sistema de origem e destino;
- terminologia, identificadores e regras de transformação;
- autenticação, transporte, retries, idempotência e auditoria;
- dados permitidos, finalidade e retenção sob LGPD;
- exemplos anonimizados e casos de aceite.

Sem esses requisitos, o status é `escopo pendente`, não `suportado`.

