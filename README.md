# S.O.F.I.A. local

Plataforma local React + FastAPI + MCP. A pasta `knowledge/` é a fonte única do conhecimento: cada subpasta é um módulo RAG e os arquivos são lidos pelo backend em tempo de execução.

## Executar

Na raiz do projeto:

```powershell
pnpm install
.venv\Scripts\python.exe -m pip install -r requirements.txt
.\start-local.ps1
```

O navegador abre em `http://127.0.0.1:5174/` e a API local em `http://127.0.0.1:8787/`. O endpoint MCP Streamable HTTP está em `http://127.0.0.1:8787/mcp`. O script `start-local.ps1` também publica o frontend e a API no endereço da máquina (`0.0.0.0`) para uso na rede interna; os computadores clientes devem abrir `http://IP-DO-SERVIDOR:5174/`.

Para liberar as portas no Firewall do Windows, abra o PowerShell como Administrador e execute `.\allow-network.ps1`. O script cria regras somente para o perfil de rede `Private`; não exponha essas portas em redes públicas.

Todos os diretórios de primeiro nível presentes em `knowledge/` são ativados automaticamente na inicialização. Hoje isso inclui Almoxarifado, Contabilidade, Departamento Pessoal, Direito, Financeiro, Gestão Empresarial, Infraestrutura, Medicina, Prefeitura, Recursos Humanos e Secretaria.

O código da conta administradora é fixo: `AG000001`. A senha inicial é lida somente de `SOFIA_ADMIN_FIRST_PASSWORD` no arquivo `.env` local e nunca fica armazenada na documentação ou na interface. Em uma base já criada para desenvolvimento, configure `SOFIA_ADMIN_RESET_PASSWORD=true` uma única vez para aplicar a senha inicial e depois volte para `false`. O banco local é `data/sofia.sqlite3`.

O login aceita o código do usuário ou o e-mail cadastrado. Novos usuários usam o botão **Solicitar acesso** na própria tela de login, sem criar senha nessa etapa. A solicitação fica pendente até a aprovação exclusiva da `AG000001`. Na aprovação, o sistema gera a matrícula com as duas primeiras letras do módulo principal e seis números incrementais (por exemplo, `IN000001`). O administrador entrega a matrícula e o token de ativação por canal seguro; o usuário cria a senha, escaneia o QR do 2FA e só então pode entrar. Um ou mais módulos podem ser liberados, ou `CORE`, que libera todos. Cada sessão é registrada, expira e pode ser revogada no logout.

Para criação administrativa direta, use `POST /api/auth/users` com `email`, `name`, `password`, `scopes` e, opcionalmente, `primary_module`; a matrícula sempre é gerada pelo servidor. Senhas definitivas exigem pelo menos 8 caracteres, com maiúscula, minúscula, número e caractere especial. A senha temporária de bootstrap do administrador é exceção controlada e obriga a troca no primeiro acesso.

## Providers

- O modo `auto` é o padrão: o RAG/MCP local é consultado primeiro; sem opt-in de privacidade, a geração fica no Ollama. Com `SOFIA_ALLOW_EXTERNAL_DATA=true` e chaves configuradas, OpenAI Responses, Gemini e Claude entram como fallback/apoio antes do Ollama. Contexto de paciente/FHIR continua preso ao Ollama até que `SOFIA_ALLOW_EXTERNAL_CLINICAL=true` seja habilitado separadamente.
- O provider OpenAI usa o SDK oficial e o endpoint Responses API. Configure `OPENAI_API_KEY` e, se necessário, `OPENAI_MODEL=gpt-5.5`. `OPENAI_STORE_RESPONSES=false` é o padrão de minimização; altere para `true` somente com a governança de retenção aprovada. A chave nunca é enviada ao navegador.
- O modelo local padrão é `qwen3.5:4b`, já adequado para esta máquina; altere `OLLAMA_MODEL` no `.env` se preferir outro modelo instalado.
- Há um instalador opcional em `install-ollama-qwen9b.ps1` para o Qwen3.8 9B quantizado do exemplo. Ele é local, mas a variante é “uncensored”; mantenha-a experimental e não a use como padrão para decisões clínicas ou jurídicas. O script não altera o `.env` automaticamente.
- O chat usa `análise estruturada` por padrão: conclusão, base documental, pontos de atenção, limites e próximo passo, omitindo blocos sem evidência. `resumo direto` continua disponível para respostas curtas e `detalhada` amplia o contexto. Os tempos são controlados por `SOFIA_STRUCTURED_TIMEOUT_SECONDS` (padrão 24 s), `SOFIA_CONCISE_TIMEOUT_SECONDS` (18 s) e `SOFIA_PROVIDER_TIMEOUT_SECONDS` (25 s).

## Fluxo real

1. O usuário envia um prompt autenticado.
2. O CORE classifica intenção e complexidade e seleciona o pacote isolado do módulo em `api/domain_packages/`.
3. O tool MCP `rag_answer` chama recuperação híbrida somente em `knowledge/<módulo>`: lexical, BM25-like, TF-IDF e embedding local quando disponível.
4. O Evidence Judge reclassifica relevância, autoridade, proveniência, suporte e conflitos; se faltar evidência, o harness faz no máximo um segundo passe de recuperação.
5. O contexto aprovado é enviado ao provider escolhido: Ollama local, OpenAI Responses, Gemini ou Claude, conforme a política de privacidade.
6. A resposta passa por crítica/verificação e retorna fontes, evidências aceitas/rejeitadas, score, provider, status e telemetria operacional.

O `Production Gate` consolida o checklist de dez níveis por módulo e bloqueia a
liberação quando houver corpus incompleto, quarentena, regressão pendente,
falha de segurança ou PostgreSQL indisponível em modo de produção. Abaixo de
100% não há “retreinamento mágico”: o painel informa a ação necessária e a
fila sequencial reprocessa somente quando uma fonte nova, uma correção ou um
treino explicitamente autorizado altera o módulo.

Perguntas clínicas são classificadas por intenção antes da busca. Por exemplo, uma queixa de sonolência, piscadas de sono ou microssono usa a fonte clínica local `knowledge/medicina/textos/clinical-sleep-guidance.md`; CID-10, CID-11 e CIF permanecem como classificações e não são usados como explicação clínica principal. A memória da conversa também incorpora acompanhamentos clínicos completos, não apenas perguntas curtas.

O idioma padrão do chat é português do Brasil. O seletor de idioma permite português-BR, inglês ou espanhol; a preferência é enviada ao prompt do provider e também aparece no retorno da API. O estilo `análise estruturada` é o padrão e organiza a resposta por conclusão, evidências, pontos de atenção, limites e próximo passo; `resumo direto` e `detalhada` continuam disponíveis.

O módulo Rede Neural usa dados reais dos chunks de `knowledge/`, treina um autoencoder isolado por módulo e persiste os pesos em `data/neural/`. Em paralelo, o Ollama local gera embeddings neurais com o modelo `OLLAMA_EMBEDDING_MODEL` (padrão `nomic-embed-text`), armazenando somente vetores e coordenadas da fonte em `data/semantic-embeddings/`. A configuração padrão indexa 100 chunks por módulo para manter uma máquina sem GPU responsiva; `SOFIA_EMBEDDING_MAX_CHUNKS=20000` permite ampliar a cobertura quando houver mais tempo/recursos. Após upload, link novo ou detecção de fonte desatualizada, o módulo entra numa fila única: embeddings e treinamento terminam antes de o próximo módulo começar (`SOFIA_AUTO_TRAIN_ON_STARTUP=true`). A tela permite treinar, consultar o status e executar inferência; os recursos estão expostos pelos tools MCP `neural_train`, `neural_status`, `neural_infer`, `semantic_embedding_status` e `semantic_embed`.

## Fontes, OCR e links

O Upload aceita documentos de texto, PDF, DOCX, XLSX, CSV, JSON, XML, YAML, LOG e imagens PNG/JPG/JPEG/WEBP/BMP/TIFF. Imagens ficam em `knowledge/<módulo>/imagens` e o texto OCR é extraído com Tesseract em português e inglês durante a indexação e o treinamento.

Links HTML, texto, JSON e XML podem ser associados a um módulo. O conteúdo é salvo como documento offline em `knowledge/<módulo>/links` para entrar no RAG e, quando `SOFIA_POSTGRES_URL` estiver preenchido, também na tabela PostgreSQL `sofia_knowledge_links`. Sem uma DSN configurada, o modo local usa `data/links.json` como fallback explícito. A opção de pesquisa densa solicita até dez páginas do mesmo domínio e informa quantas foram realmente lidas; domínios que não expõem dez links não são preenchidos artificialmente.

### Expansão contínua

Cada pergunta cria um tema semântico anonimizado e uma tarefa persistente. Com PostgreSQL válido, o runtime usa o schema isolado `sofia_runtime`; o SQLite (`data/knowledge_expansion.sqlite3`) só é permitido no modo `SOFIA_STORAGE_MODE=developer`. Em produção, a indisponibilidade do PostgreSQL bloqueia o fluxo. Consultas equivalentes são agrupadas, recebem prioridade por frequência/recência e podem ser expandidas pelo ciclo automático. A expansão pesquisa fontes públicas, seleciona domínios confiáveis por módulo, respeita `robots.txt`, normaliza URLs, elimina duplicatas, captura no máximo dez páginas por tema e grava cada snapshot offline em `knowledge/<módulo>/links`.

O crawler permanece no domínio permitido da fonte e não atravessa autenticação, paywall, captcha ou bloqueios. Links descobertos não são aceitos automaticamente quando não passam pelo filtro de relevância; o administrador pode liberar ou bloquear um domínio em `POST /api/admin/expansion/domains`. O painel administrativo do Dashboard permite executar, pausar, retomar e reprocessar a fila. Estados de fonte e documento incluem `PENDING`, `UPDATING`, `READY`, `PARTIAL`, `FAILED` e `QUARANTINED`. Falhas são isoladas por arquivo e não interrompem os demais módulos.

O schema institucional de referência está em `migrations/001_knowledge_expansion.sql`; o adaptador de runtime cria a versão compatível no schema `sofia_runtime` quando `SOFIA_POSTGRES_URL` ou `DATABASE_URL` autentica com sucesso. A mesma rotina registra versões, hashes, validadores HTTP, jobs, erros e testes de recuperação. O treinamento neural e os embeddings continuam sequenciais por módulo e só são agendados depois de uma fonte publicada com sucesso. O endpoint administrativo informa explicitamente se está em `postgresql` ou `sqlite-fallback`, sem exibir credenciais.

## Analista e FHIR

O tool MCP `analyst_scenario` combina evidência RAG, provider LLM, amostragem aleatória, inferência neural quando treinada e simulação Monte Carlo. O painel do dashboard aceita um tema documentado para executar essa análise. O resultado é apoio à decisão, não previsão garantida.

## Integrações institucionais

A camada isolada `api/integrations.py` começa pelo TASY e mantém o contrato para Protheus, Lyceum, Fluig, drives de rede, AD e portal Microsoft. A implementação só executa conectores que tenham endpoint, credencial e escopo configurados; não simula dados. A base de ingestão trabalha com leitura paginada, jobs, RAW local, detecção de registro novo/alterado/inalterado, checkpoints e DLQ. O status está em `GET /api/integrations`, a sincronização administrativa em `POST /api/integrations/tasy/sync` e os tools MCP são `institutional_integration_status` e `institutional_integration_sync`. Para ativar o TASY, configure `SOFIA_TASY_BASE_URL` e `SOFIA_TASY_TOKEN` no `.env`; sem essas variáveis, o conector permanece claramente como não configurado. Novos adaptadores devem normalizar os registros para o módulo correto e entrar na mesma fila sequencial de treinamento.

O servidor expõe um armazenamento local compatível com FHIR R4 em `/fhir/metadata`, `/fhir/{ResourceType}` e `/fhir/{ResourceType}/{id}`, com `Patient`, `Observation`, `Condition`, `Encounter`, `DiagnosticReport`, `CarePlan`, `MedicationRequest` e outros recursos habilitados. Leitura exige autenticação; gravação exige usuário `admin` ou `clinician`. Sugestões clínicas devem ser revisadas por profissional habilitado e não são prescrições automáticas.

A página `Conexões & Fluxos` mostra o estado real do MCP, RAG, OCR, PostgreSQL, FHIR, providers e controles de privacidade. Ela explica o que cada parametrização altera: estilo muda o tamanho da saída; pesquisa densa muda a quantidade de páginas offline; provider muda o motor; treinamento automático atualiza a rede após novas fontes. O sistema registra auditoria sem guardar prompts, documentos ou valores clínicos no log. Para PostgreSQL, configure `SOFIA_POSTGRES_URL` no `.env` e reinicie a API.

Para a conta `AG000001`, o `Pipeline Explorer` acompanha documentos, etapas,
qualidade, OCR, chunks, traces e insights por módulo. A avaliação técnica
reprodutível também pode ser executada pelo script `python scripts/run_evals.py`
ou por `GET /api/admin/evaluation`; ela mede disponibilidade e recuperação do
corpus, sem inventar uma nota de qualidade para respostas que ainda não foram
revisadas por especialistas.

O Dashboard registra estatísticas de temas consultados numa biblioteca isolada (`api/analytics.py`). Com `SOFIA_POSTGRES_URL` ou `DATABASE_URL`, a tabela `sofia_query_analytics` do PostgreSQL é a principal; sem conexão disponível, `data/agent_memory.sqlite3` é o fallback local. São armazenados apenas matrícula, módulo, tema semântico, intenção, quantidade de fontes, provider, verificação, horário e feedback; perguntas, respostas e conteúdo clínico não são gravados. O usuário pode marcar uma resposta como útil, não útil ou não responder (mediana). “Não útil” oferece uma nova tentativa no chat, mas uma ampliação externa com dados sensíveis continua exigindo autorização. A API `GET /api/analytics/themes?module_id=medicina&days=30` e `POST /api/analytics/feedback` exigem sessão; as estatísticas exigem especificamente a conta `AG000001`. O relatório não é exposto como ferramenta MCP pública para evitar que outro cliente contorne essa regra.

As ferramentas MCP isoladas são `list_knowledge_modules`, `search_knowledge`, `rag_answer`, `analyst_scenario`, `tensor_multiply`, `random_generate`, `neural_train`, `neural_status`, `neural_infer`, `neural_graph`, `knowledge_graph`, `semantic_embedding_status`, `semantic_embed`, `monte_carlo_estimate`, `production_gate`, `institutional_integration_status` e `institutional_integration_sync`. `knowledge_graph` e `production_gate` exigem capacidade administrativa. Estatísticas são uma função administrativa da API autenticada, não uma ferramenta MCP pública.
