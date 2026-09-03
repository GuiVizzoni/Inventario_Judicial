# Registro de alterações e acréscimos

Data de referência: 2 de setembro de 2026. Estado anterior: protótipo de telas em Next.js com dados fixos no código, sem backend. Estado atual: backend em FastAPI completo com adaptador de IA em mock, e as nove telas consumindo a API.

## 1. Backend (pasta `backend/`, inteiramente nova)

### Infraestrutura

| Arquivo | O que faz |
|---|---|
| `requirements.txt` | dependências fixadas: FastAPI, Uvicorn, SQLAlchemy 2, Alembic, Pydantic 2, pydantic-settings, python-multipart, PyMuPDF, pytesseract, Pillow, PyJWT, bcrypt, psycopg, httpx, pytest |
| `.env.example` | todas as variáveis de ambiente com valores padrão |
| `.gitignore` | ignora `.venv`, caches, `*.db`, `uploads/`, `exemplos/`, `.env`, logs |
| `docker-compose.yml` | PostgreSQL 16 com usuário, senha e banco `inventario` |
| `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako` | configuração de migrações lendo `DATABASE_URL` da aplicação |
| `alembic/versions/9175764a1cd5_inicial.py` | revisão inicial com as oito tabelas, gerada por autogenerate e verificada com `upgrade head` |

### Aplicação (`backend/app/`)

| Arquivo | O que faz |
|---|---|
| `main.py` | instância do FastAPI, CORS, `create_all` na inicialização, handler global de erros de domínio, registro dos routers, rota de saúde `/` |
| `config.py` | classe `Configuracao` (pydantic-settings) com banco, JWT, CORS, uploads, provedor de LLM, OCR |
| `db.py` | engine, `SessionLocal`, `Base` e dependência `obter_sessao` |
| `dominio/enums.py` | `StatusItem`, `StatusProcesso`, `TipoDocumento`, `OrigemDocumento`, `CategoriaPendencia`, `CategoriaEntidade`, `CategoriaBem`, `OrigemBem`, `PapelUsuario`, `TipoEvento` |
| `dominio/catalogo_documentos.py` | doze tipos documentais com nome, categoria, bloqueante, obrigatório, origem, link do portal e tutorial |
| `models/base.py` | classe base com `id` UUID e `criado_em` |
| `models/usuario.py`, `processo.py`, `documento.py`, `herdeiro.py`, `bem.py`, `entidade_extraida.py`, `pendencia.py`, `evento.py` | as oito tabelas |
| `repositories/base.py` e um arquivo por tabela | acesso ao banco com consultas específicas (por processo, por tipo, validados, última versão, recentes) |
| `services/excecoes.py` | `ErroServico`, `NaoEncontrado`, `AcessoNegado`, `RegraDeNegocio` |
| `services/auth_service.py` | hash bcrypt, JWT, autenticação e criação de usuário |
| `services/ingestao.py` | extração de texto de PDF com PyMuPDF, OCR opcional e normalização |
| `services/nlp_service.py` | `NLPService`: classificação e extração via adaptador, validação pelo esquema Pydantic, gravação versionada das entidades |
| `services/diagnostico_service.py` | `DiagnosticoService`: regras de inconsistência, sincronização de pendências, árvore genealógica, resumo da análise e recomendação |
| `services/processo_service.py` | `ProcessoService`: criação com pendências obrigatórias, desbloqueio, checklist, resumo, CRUD de herdeiros e bens, eventos, resolução manual de pendência |
| `services/documento_service.py` | `DocumentoService`: upload, pipeline completo, reprocessamento, remoção, busca automática de certidões, função para execução em segundo plano |
| `integrations/llm_adapter.py` | contrato `LLMAdapter` e dataclasses `ResultadoClassificacao` e `ResultadoExtracao` |
| `integrations/llm_mock.py` | `MockLLMAdapter` heurístico |
| `integrations/llm_openai.py` | `OpenAILLMAdapter` com métodos a implementar pelo módulo de IA |
| `integrations/certidao_adapter.py` | contrato `CertidaoAdapter` e `MockCertidaoAdapter` que gera PDFs de CND fictícias |
| `integrations/fabrica.py` | escolha do adaptador por configuração |
| `nlp/esquemas.py` | dez esquemas Pydantic de extração com categoria e sinônimos por campo, mais funções de consulta |
| `api/deps.py` | dependências `usuario_atual` (Bearer JWT) e `processo_atual` (verifica dono) |
| `api/schemas/__init__.py` | modelos de entrada e saída de todos os endpoints; datas sem fuso recebem UTC explícito na serialização |
| `api/routers/auth.py` | login, usuário atual, criação de usuário por administrador |
| `api/routers/catalogo.py` | listagem do catálogo documental |
| `api/routers/processos.py` | CRUD de processo, resumo, checklist, eventos |
| `api/routers/documentos.py` | listagem, upload multipart, busca automática, detalhe, download, reprocessar, remover |
| `api/routers/herdeiros.py`, `bens.py` | CRUD |
| `api/routers/pendencias.py` | listagem e resolução manual |
| `api/routers/diagnostico.py` | análise, execução do diagnóstico, árvore |

### Scripts e testes

| Arquivo | O que faz |
|---|---|
| `scripts/gerar_pdfs_exemplo.py` | funções que geram PDFs fictícios por tipo documental e o dicionário `EXEMPLOS` usado pelo seed e pelos testes; executado direto, grava os arquivos em `backend/exemplos/` |
| `scripts/seed.py` | cria dois usuários, um inventário completo e processa oito documentos; aceita `--reset` |
| `tests/conftest.py` | banco SQLite temporário, pasta de uploads temporária, usuários de teste, `TestClient` e tokens |
| `tests/test_api.py` | seis testes de integração (todos passando) |

## 2. Frontend

### Arquivos novos

| Arquivo | O que faz |
|---|---|
| `lib/api.js` | cliente HTTP com token no `localStorage`, tratamento de 401 (volta ao login), mensagens de erro do FastAPI, download autenticado e funções por recurso (`auth`, `catalogo`, `processos`, `documentos`, `herdeiros`, `bens`, `pendencias`, `analise`) |
| `lib/formatadores.js` | data, data e hora, tempo relativo, moeda, tamanho de arquivo, iniciais, categorias de bem |
| `lib/useDados.js` | hook que carrega dados de uma função assíncrona e expõe `dados`, `erro`, `carregando`, `recarregar` |
| `components/SessaoProvider.js` | contexto global com usuário logado, lista de processos, processo selecionado (persistido no `localStorage`), `entrar`, `sair`; redireciona para `/login` sem token |
| `components/Campo.js` | `Campo`, `Selecao`, `Alerta`, `BotaoPrimario`, `BotaoSecundario` |
| `components/SemProcesso.js` | estado vazio com link para o cadastro |
| `.env.example` | `NEXT_PUBLIC_API_URL` |

### Arquivos alterados

| Arquivo | Antes | Depois |
|---|---|---|
| `app/layout.js` | fontes e metadata | envolve a aplicação no `SessaoProvider` |
| `components/Navbar.js` | nome e processo fixos | nome, papel e iniciais do usuário logado; número ou nome do processo selecionado; clique no avatar faz logout |
| `app/login/page.js` | qualquer credencial redirecionava | chama `POST /auth/login`, mostra erro, redireciona quem já está logado |
| `app/central/page.js` | constantes mockadas | consome `GET /processos/{id}/resumo`; seletor de processo quando há mais de um; selo de situação conforme status; atividades vindas dos eventos |
| `app/inventario/novo/page.js` | formulário sem estado | três etapas com estado, envio de certidão de óbito opcional, `POST /processos` e upload em seguida, seleção automática do novo processo |
| `app/documentos/page.js` | tabela fixa | lista da API, painel de upload com tipos do catálogo, busca automática de CNDs, abrir, reprocessar, excluir, painel de detalhe com entidades extraídas e texto |
| `app/documentos/checklist/page.js` | lista fixa | checklist da API com rótulo bloqueante/obrigatório/complementar, tutorial e link do portal para itens pendentes |
| `app/herdeiros/page.js` | cards fixos | lista da API, formulário de cadastro (com cônjuge, pré-morto e representação), remoção, detalhes |
| `app/patrimonio/page.js` | tabela fixa | lista da API, formulário de declaração, confirmação e remoção, total calculado |
| `app/arvore-genealogica/page.js` | HTML fixo | renderiza a estrutura de `GET /processos/{id}/arvore`, incluindo representantes de pré-mortos e observações geradas |
| `app/analise-ia/page.js` | lista fixa | consome `GET /processos/{id}/analise`, botão para executar nova análise |
| `README.md` | instruções do protótipo | instruções de backend e frontend, credenciais do seed, estrutura, aviso sobre repositório público |

Arquivos do protótipo mantidos sem alteração: `components/Card.js`, `components/Selo.js`, `components/ProgressoDocumental.js`, `app/page.js`, `app/globals.css`, configurações do Next e Tailwind, `package.json`.

## 3. Documentação nova

- `docs/BACKEND.md`: arquitetura, modelo de dados, pipeline, diagnóstico, endpoints, encaixe da IA.
- `docs/ALTERACOES.md`: este arquivo.

## 4. Como o módulo de IA se encaixa

1. Implementar `classificar` e `extrair` em `backend/app/integrations/llm_openai.py`, usando os esquemas de `backend/app/nlp/esquemas.py` como saída estruturada.
2. Definir `LLM_PROVIDER=openai` e `OPENAI_API_KEY` no `.env`.
3. Rodar `python -m pytest`. Os testes usam o mock por padrão; para testar o adaptador real, criar testes próprios com PDFs fictícios gerados por `scripts/gerar_pdfs_exemplo.py`.

Nenhum outro arquivo precisa mudar. As métricas de tempo e modelo já são gravadas em `documento.processamento_*` e `entidade_extraida.duracao_ms` e `modelo_llm`.

## 5. O que não foi feito

- Adaptador real de LLM (responsabilidade do módulo de IA).
- Adaptador real de certidões negativas (portais públicos); hoje é simulado.
- Recuperação de senha e cadastro de usuário pela tela (só via API por administrador ou pelo seed).
- Build de produção do frontend não foi executado nesta sessão; o servidor de desenvolvimento foi validado em todas as telas.
