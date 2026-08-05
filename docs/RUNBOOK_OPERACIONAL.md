# Runbook operacional da SOFIA

Este é o roteiro oficial para configurar, atualizar, validar e recuperar a plataforma. Execute os comandos a partir de `/opt/sofia` e nunca registre valores do `.env` em chamados, capturas, commits ou logs compartilhados.

## 1. Pré-requisitos e arquivos locais

- Docker Engine com Compose v2.
- Git.
- `.env` somente no servidor, criado a partir de `.env.example`.
- DNS ou acesso por IP apontando para a porta publicada da API.

O `.env`, arquivos `.env.*`, logs, dados e caches de conhecimento estão no `.gitignore`. O arquivo versionado `.env.example` contém apenas nomes e exemplos seguros. As conexões do PostgreSQL, Zabbix, Grafana, SMTP, Claude e Ollama devem permanecer exclusivamente no `.env` local.

Validação sem revelar valores:

```bash
git check-ignore -v .env
git ls-files | grep -E '(^|/)\.env$' && echo "ERRO: .env rastreado" || echo "OK: .env não rastreado"
```

## 2. Primeiro acesso

1. Abra `/login.html`; a raiz `/` redireciona para o login.
2. O administrador inicial `glauco.almeida` começa pendente e sem senha.
3. Use **Configurar primeiro acesso**.
4. Cadastre e-mail de recuperação e senha com pelo menos oito caracteres, maiúscula, minúscula e símbolo.
5. Leia o QR Code com o Google Authenticator e confirme o TOTP.
6. Novos usuários usam **Solicitar acesso** e aguardam aprovação do administrador.

Senhas são armazenadas como hash e nunca ficam visíveis, inclusive para administradores. Em caso de esquecimento, o administrador autoriza a redefinição; ele não consulta a senha anterior.

## 3. Operação diária

```bash
docker compose ps
curl -fsS http://127.0.0.1:8080/health
curl -fsS http://127.0.0.1:8080/mcp/health
```

Interfaces:

- Início: saúde, recursos, provedores e atividade de aprendizado.
- Base: fontes e documentos da base offline (administrador).
- Conversar: consultas de informática, base local, Zabbix e fallback Claude/Ollama.
- Automação: editor de blocos, execução, timeline, gráficos e relatórios.
- Gestão: usuários, aprovações, perfis e sessões (somente administrador).
- Perfil: dentro do menu do nome do usuário.

## 4. Fluxo de IA e conhecimento

```text
Pergunta de informática
  → busca offline
  → ferramentas autorizadas (por exemplo Zabbix)
  → Claude quando falta conhecimento local
  → Ollama como fallback
  → resposta, auditoria e ciclo de aprendizado
```

Assuntos fora de informática são recusados e encaminhados ao administrador para inclusão de base. O aprendizado contínuo persiste perguntas, respostas, snapshots e padrões; isso não significa retreinar automaticamente os pesos do Claude.

O Zabbix é coletado periodicamente. O painel analítico usa:

- baseline e recorrência;
- Monte Carlo, após oito amostras limpas;
- Random Forest, após vinte amostras limpas;
- TensorFlow opcional, após 24 amostras e somente em CPU com AVX.

O servidor atual não possui AVX. A integração TensorFlow fica corretamente marcada como incompatível e não é carregada, evitando queda da API. Em hardware compatível, use `api/requirements-tensorflow.txt`.

## 5. Criar e executar automação

1. Arraste um bloco para o canvas ou selecione-o e clique no canvas.
2. Conecte a saída verde de um bloco à entrada azul do próximo.
3. Para Zabbix, use `Alerta/pergunta → Zabbix → Gerar relatório`.
4. Salve e valide o fluxo.
5. Informe a pergunta em **Respostas e relatórios** e execute.
6. Confira timeline, hosts únicos, grupos, severidades, gráficos, baseline e relatório.

Hosts em vários grupos são consolidados pelo `hostid`, portanto não são contados duas vezes.

## 6. Atualização segura do Docker

Não use `docker compose down -v`. O sufixo `-v` remove volumes e pode destruir PostgreSQL, Grafana, Qdrant, Ollama, Prometheus, Loki e n8n.

Procedimento recomendado:

```bash
cd /opt/sofia
docker compose pull
docker compose up -d --build
docker compose ps
```

O `pull` atualiza imagens externas. A API é construída do código local. O `up -d` recria somente o necessário e preserva os volumes nomeados.

Depois da atualização:

```bash
curl -fsS http://127.0.0.1:8080/health
curl -fsS http://127.0.0.1:8080/mcp/health
docker compose exec -T sofia-api pytest -q
```

## 7. Git sem segredos

Antes de cada commit:

```bash
git status --short
git diff --check
git diff --cached --stat
git check-ignore -v .env
```

Fluxo local:

```bash
git add <arquivos explícitos>
git commit -m "tipo: descrição objetiva"
```

Não use `git add .` antes de revisar. Não faça push sem autorização. Nunca inclua `.env`, tokens, senhas, URLs privadas com credenciais, dumps do banco, chaves TOTP ou arquivos de sessão.

Se um segredo for incluído por engano, interrompa o push, remova-o do índice, faça rotação imediata da credencial e audite o histórico. Apenas apagar o arquivo em um commit posterior não elimina o segredo do histórico.

## 8. Backup e rollback

Antes de mudanças de banco ou upgrades maiores, gere backup fora do repositório. Não coloque dumps em `docs/` ou em outra pasta versionada.

Para voltar apenas a imagem/código da API, selecione um commit conhecido e reconstrua sem remover volumes. Para serviços externos, prefira fixar temporariamente uma versão conhecida no Compose e executar `docker compose up -d <serviço>`.

## 9. Diagnóstico rápido

- `401/403`: valide sessão, perfil, TOTP e expiração por inatividade.
- Claude indisponível: confira no painel o estado da chave/modelo/crédito; Ollama permanece como fallback.
- Zabbix sem resposta: valide URL, usuário, conectividade e se o fluxo contém o bloco Zabbix.
- Resultado duplicado: confirme que a resposta lista hosts únicos por `hostid`; grupos múltiplos devem aparecer dentro do mesmo host.
- Modelo preditivo coletando: aguarde o número mínimo de snapshots limpos indicado no painel.
- TensorFlow incompatível: requer CPU com AVX; Random Forest e Monte Carlo continuam operacionais.

## 10. Checklist de entrega

- [ ] `.env` existe somente localmente e está ignorado.
- [ ] Nenhum segredo aparece no diff ou no histórico.
- [ ] `docker compose pull` terminou sem erro.
- [ ] `docker compose up -d --build` terminou sem remover volumes.
- [ ] Containers esperados estão `Up`/`healthy`.
- [ ] `/health` e `/mcp/health` respondem.
- [ ] PostgreSQL aceita a conexão da aplicação.
- [ ] Testes automatizados passam.
- [ ] Alterações estão em commit local claro.
- [ ] Push remoto só ocorre após autorização explícita.
