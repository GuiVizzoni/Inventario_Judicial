# Plataforma de Inventário Judicial

Sistema em duas partes, no mesmo repositório:

| Parte | Tecnologia | Pasta | Porta |
|---|---|---|---|
| Frontend (9 telas) | Next.js 14 (App Router) + React + Tailwind CSS | raiz (`app/`, `components/`, `lib/`) | 3000 |
| Backend (API REST + pipeline documental) | Python 3.12+ / FastAPI / SQLAlchemy / PostgreSQL ou SQLite | `backend/` | 8000 |

O frontend consome exclusivamente a API do backend. Não há mais dados mockados nas telas.

Documentação detalhada:

- [docs/BACKEND.md](docs/BACKEND.md): arquitetura, modelo de dados, pipeline de documentos, regras de diagnóstico, endpoints e ponto de encaixe da IA.
- [docs/ALTERACOES.md](docs/ALTERACOES.md): registro de tudo que foi criado e alterado, arquivo por arquivo.

## Pré-requisitos

- Node.js 18.18 ou superior e npm
- Python 3.12 ou superior
- Opcional: Docker (para PostgreSQL) e Tesseract OCR (para PDFs digitalizados)

## Rodando o backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

No Linux ou macOS, troque `.venv\Scripts\activate` por `source .venv/bin/activate` e `copy` por `cp`.

- Sem nenhuma configuração, o backend usa um arquivo SQLite (`backend/inventario.db`). Para PostgreSQL, suba o banco com `docker compose up -d` dentro de `backend/` e aponte `DATABASE_URL` no `.env` para `postgresql+psycopg://inventario:inventario@localhost:5432/inventario`.
- O seed cria dois usuários e um inventário completo, com documentos fictícios já processados:
  - `ana.ramos@escritorio.com.br` / `inventario123` (administradora)
  - `guilherme@escritorio.com.br` / `inventario123` (advogado)
- Documentação interativa da API: `http://localhost:8000/docs`.
- Testes: `python -m pytest` dentro de `backend/`.

## Rodando o frontend

```bash
npm install
npm run dev
```

Acesse `http://localhost:3000`. A raiz redireciona para `/login`. A URL da API é lida de `NEXT_PUBLIC_API_URL` (padrão `http://localhost:8000`; veja `.env.example`).

## Rotas do frontend

| Tela | Rota |
|---|---|
| Login | `/login` |
| Central do Inventário | `/central` |
| Cadastro Inicial do Inventário | `/inventario/novo` |
| Checklist Documental | `/documentos/checklist` |
| Gerenciamento de Documentos | `/documentos` |
| Gestão de Herdeiros | `/herdeiros` |
| Gestão Patrimonial | `/patrimonio` |
| Árvore Genealógica Automatizada | `/arvore-genealogica` |
| Análise Inteligente do Inventário | `/analise-ia` |

## Identidade visual

- Cores: tons de tinta/navy (`ink`), papel (`parchment`) e bronze.
- Tipografia: Source Serif 4 (títulos), Inter (texto) e IBM Plex Mono (códigos e valores).
- Selo: badge de status reutilizado em todas as telas (`concluido`, `em_analise`, `pendente`, `rejeitado`, `nao_iniciado`). Os mesmos cinco valores são o enum de status do backend.

## Estrutura

```
.
├── app/                     telas (Next.js App Router)
├── components/              Navbar, Card, Selo, ProgressoDocumental, Campo, SemProcesso, SessaoProvider
├── lib/                     api.js (cliente HTTP), formatadores.js, useDados.js
├── backend/
│   ├── app/                 código da API (ver docs/BACKEND.md)
│   ├── alembic/             migrações de banco
│   ├── scripts/             seed e gerador de PDFs fictícios
│   ├── tests/               testes de integração da API
│   ├── docker-compose.yml   PostgreSQL local
│   └── requirements.txt
└── docs/
```

## Repositório público

Nunca versione `.env`, a pasta `backend/uploads/`, arquivos `.db` nem documentos reais de processos. Tudo isso já está no `.gitignore`. Os PDFs usados no seed e nos testes são gerados por `backend/scripts/gerar_pdfs_exemplo.py` e contêm apenas dados fictícios.
