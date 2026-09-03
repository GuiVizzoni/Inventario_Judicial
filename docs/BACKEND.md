# Backend: arquitetura e lógica

Este documento descreve a camada de backend construída para a Plataforma de Inventário Judicial. Ele segue a proposta técnica da monografia (capítulos 3 e 4) e aponta, em cada ponto, o que foi implementado exatamente como descrito e o que foi acrescentado para que as telas do frontend funcionem.

## 1. Visão geral

O backend é uma aplicação Python com FastAPI, organizada como monolito modular em quatro camadas com dependência unidirecional (API → Serviços → Integrações e Persistência). Ele recebe documentos em PDF, extrai o texto, classifica o documento, extrai entidades estruturadas, cruza os dados extraídos com o formulário preenchido pelo advogado, mantém o estado do processo (bloqueado, aberto, concluído) e expõe tudo por REST para o frontend Next.js.

A camada de IA não está implementada. Existe um contrato (`LLMAdapter`) e uma implementação heurística (`MockLLMAdapter`) que permite rodar todo o fluxo de ponta a ponta sem chave de API. A pessoa responsável pela IA precisa entregar apenas uma classe que respeite esse contrato.

## 2. Estrutura de pastas

```
backend/
├── app/
│   ├── main.py                  cria o FastAPI, CORS, handler de erros, registra os routers
│   ├── config.py                configuração via variáveis de ambiente (pydantic-settings)
│   ├── db.py                    engine, sessão e Base do SQLAlchemy
│   ├── dominio/
│   │   ├── enums.py             todos os enums do sistema
│   │   └── catalogo_documentos.py   catálogo dos tipos documentais (nome, bloqueante, origem, link do portal, tutorial)
│   ├── models/                  tabelas (SQLAlchemy 2.0, tipagem Mapped)
│   ├── repositories/            acesso ao banco, uma classe por tabela
│   ├── services/                regras de negócio
│   │   ├── processo_service.py      ProcessoService
│   │   ├── documento_service.py     DocumentoService (ingestão e orquestração do pipeline)
│   │   ├── nlp_service.py           NLPService
│   │   ├── diagnostico_service.py   DiagnosticoService (inconsistências e árvore)
│   │   ├── ingestao.py              extração de texto de PDF (PyMuPDF, OCR opcional)
│   │   ├── auth_service.py          senhas (bcrypt) e JWT
│   │   └── excecoes.py              erros de domínio mapeados para HTTP
│   ├── integrations/
│   │   ├── llm_adapter.py           contrato LLMAdapter e dataclasses de resultado
│   │   ├── llm_mock.py              MockLLMAdapter (palavras-chave + pares rótulo/valor)
│   │   ├── llm_openai.py            OpenAILLMAdapter (esqueleto; a implementar pelo módulo de IA)
│   │   ├── certidao_adapter.py      contrato CertidaoAdapter e MockCertidaoAdapter
│   │   └── fabrica.py               escolhe o adaptador conforme LLM_PROVIDER / CERTIDAO_PROVIDER
│   ├── nlp/
│   │   └── esquemas.py              esquemas Pydantic de extração, um por tipo documental
│   └── api/
│       ├── deps.py                  usuário autenticado e processo do usuário
│       ├── schemas/__init__.py      modelos de entrada e saída da API
│       └── routers/                 auth, catalogo, processos, documentos, herdeiros, bens, pendencias, diagnostico
├── alembic/                     migrações (uma revisão inicial gerada)
├── scripts/
│   ├── gerar_pdfs_exemplo.py    gera PDFs fictícios com o layout que o mock sabe ler
│   └── seed.py                  cria usuários, um inventário completo e processa 8 documentos
├── tests/                       testes de integração com TestClient e SQLite temporário
├── docker-compose.yml           PostgreSQL 16
├── .env.example
└── requirements.txt
```

Regra de dependência: `api` importa `services`; `services` importa `repositories`, `integrations` e `models`; `repositories` importa `models`; nada abaixo importa o que está acima. A exceção deliberada é `services/processo_service.py`, que reutiliza os modelos Pydantic de entrada definidos em `api/schemas`, para não duplicar validação.

## 3. Configuração

Todas as opções vêm de variáveis de ambiente ou do arquivo `.env` (veja `.env.example`):

| Variável | Padrão | Uso |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./inventario.db` | SQLite para rodar sem instalar nada; PostgreSQL via `postgresql+psycopg://...` |
| `JWT_SECRET`, `JWT_EXPIRACAO_MINUTOS` | valor de exemplo, 480 | assinatura e validade do token |
| `CORS_ORIGINS` | `http://localhost:3000` | origens permitidas, separadas por vírgula |
| `UPLOAD_DIR` | `uploads` | onde os PDFs são gravados (`uploads/<processo_id>/<uuid>_<nome>.pdf`) |
| `LLM_PROVIDER` | `mock` | `mock` ou `openai` |
| `LLM_MODELO`, `OPENAI_API_KEY` | `gpt-4o`, vazio | usados apenas quando `LLM_PROVIDER=openai` |
| `OCR_LIMIAR_CARACTERES`, `OCR_IDIOMA` | 200, `por` | heurística de PDF digitalizado e idioma do Tesseract |
| `CERTIDAO_PROVIDER` | `mock` | reservado para o adaptador real de certidões |

Os enums são gravados como texto (`native_enum=False`) e as chaves são UUID, para que o mesmo código rode em SQLite e PostgreSQL.

## 4. Modelo de dados

As cinco tabelas do diagrama da monografia foram mantidas com os campos originais. Três tabelas de apoio e alguns campos foram acrescentados.

### Tabelas da monografia

**processo**: `numero_processo`, `status` (`bloqueado`, `aberto`, `concluido`), `data_abertura`, `data_obito`, `nome_de_cujus`, `cpf_de_cujus`, `regime_bens`, `criado_em`. Acrescentados: `ultimo_domicilio` (usado na busca de certidões estaduais e municipais) e `responsavel_id` (advogado dono do processo).

**documento**: `tipo`, `nome_arquivo`, `status_validacao`, `texto_extraido`, `origem` (`upload_manual`, `busca_automatica`), `recebido_em`. Acrescentados: `tipo_detectado` (o que o modelo achou que o arquivo era), `caminho_arquivo`, `tamanho_bytes`, `motivo_status` (explicação legível do resultado), `metodo_extracao` (`nativo`, `ocr`, `nativo_insuficiente`), `processamento_iniciado_em`, `processamento_concluido_em` e `erro_processamento`. Os três últimos são a base das métricas de tempo previstas para o capítulo 5.

**herdeiro**: `nome`, `cpf`, `parentesco`, `pre_morto`, `conjuge`. Acrescentados: `status` (confirmação documental do vínculo) e `representa_herdeiro_id`, auto-relacionamento que indica qual herdeiro pré-morto este herdeiro representa (direito de representação, art. 1.851 do Código Civil). Sem esse campo a árvore genealógica não consegue montar a linha de representação.

**entidade_extraida**: `documento_id`, `categoria`, `chave`, `valor`, `confianca`, `modelo_llm`, `extraido_em`. Acrescentados: `versao_extracao` (cada reprocessamento gera uma nova versão sem apagar as anteriores, como pede a seção 4.6) e `duracao_ms`.

**pendencia**: `tipo_documento`, `bloqueante`, `link_portal`, `resolvida`, `criado_em`. Acrescentados: `categoria` (`documento_ausente`, `documento_invalido`, `inconsistencia`), `titulo`, `descricao`, `documento_id` e `resolvida_em`. A categoria `inconsistencia` é o que a tela de Análise IA lista como resultado do diagnóstico; assim não foi preciso criar uma sexta tabela principal.

### Tabelas de apoio

**usuario**: `nome`, `email`, `senha_hash` (bcrypt), `papel` (`advogado`, `administrador`), `oab`, `ativo`.

**bem**: `descricao`, `categoria` (`imovel`, `imovel_rural`, `movel`, `financeiro`, `outro`), `valor_estimado`, `identificador` (matrícula, placa, conta), `origem` (`formulario`, `documento`), `status`. Guarda a "declaração preliminar de bens" do formulário inicial e alimenta a tela de patrimônio e a verificação de colação.

**evento**: `tipo`, `descricao`, `status`, `referencia_id`, `ator`, `criado_em`. Linha do tempo do processo, exibida na Central como "atividade recente". Também é a trilha de auditoria da seção 4.1.

### Enum de status

Um único enum `StatusItem` é usado por documento, herdeiro, bem, evento e checklist: `nao_iniciado`, `pendente`, `em_analise`, `concluido`, `rejeitado`. São exatamente os cinco valores do componente `Selo` do frontend. A correspondência com a monografia é: PENDENTE = `pendente`, INVÁLIDO = `rejeitado`, validado = `concluido`.

## 5. Catálogo documental

`app/dominio/catalogo_documentos.py` é a implementação da seção 3.2. Cada item tem tipo, nome, categoria, se é bloqueante, se é obrigatório, origem (upload manual ou busca automática), link do portal e um tutorial curto. Doze tipos estão cadastrados:

- Obrigatórios: certidão de óbito (única bloqueante), CND federal, estadual e municipal (busca automática), certidão do CENSEC, certidão de matrícula.
- Complementares: certidão de casamento, certidão de nascimento, RG e CPF, extrato bancário, CRLV, declaração de IRPF.

Quando um processo é criado, cada item obrigatório vira uma pendência `documento_ausente`. O checklist da tela é calculado a partir do catálogo cruzado com os documentos recebidos.

## 6. Ciclo de vida do processo

1. `POST /processos` recebe de cujus, herdeiros e bens. O processo nasce `bloqueado`, com as pendências obrigatórias criadas e um evento `processo_criado`.
2. Enquanto bloqueado, a busca automática de certidões é recusada (HTTP 422) e a recomendação da análise pede a certidão de óbito.
3. Quando uma certidão de óbito é validada pelo pipeline, o processo passa a `aberto`, recebe `data_abertura`, e a busca automática das três CNDs é disparada imediatamente (fluxo da Figura 1 da monografia).
4. A cada documento validado, o diagnóstico roda de novo e sincroniza as inconsistências.
5. O status `concluido` existe no enum e pode ser definido via `PATCH /processos/{id}`, mas nenhuma regra automática o atribui, porque a decisão de avançar para a partilha é do profissional.

## 7. Pipeline de documentos

Implementado em `DocumentoService.processar`, chamado em segundo plano após o upload (`BackgroundTasks` do FastAPI) e de forma síncrona pelo seed, pelos testes e pela busca automática.

1. **Recepção** (`receber_upload`): só aceita `.pdf`, até 25 MB. Grava o arquivo em disco, cria o registro com status `pendente` e um evento `documento_recebido`.
2. **Ingestão** (`services/ingestao.py`): extrai o texto com PyMuPDF. Se o total de caracteres ficar abaixo de `OCR_LIMIAR_CARACTERES`, tenta OCR com Tesseract via pytesseract. Se o Tesseract não estiver instalado, segue com o texto nativo e marca `metodo_extracao = nativo_insuficiente`. O texto é normalizado (espaços, quebras de linha, caracteres nulos) e gravado em `texto_extraido`.
3. **Classificação** (`NLPService.classificar`): o adaptador devolve o tipo detectado e a confiança. Se for diferente do tipo informado no upload, o documento fica `rejeitado`, `motivo_status` explica a divergência, uma pendência `documento_invalido` é criada e o pipeline para. É a etapa 1 da seção 4.4.
4. **Extração** (`NLPService.extrair_e_persistir`): o adaptador recebe o texto, o tipo e o esquema Pydantic daquele tipo. A resposta é validada pelo esquema (respostas malformadas geram erro e não são gravadas) e cada campo preenchido vira uma linha em `entidade_extraida`, com categoria, confiança, modelo, versão e duração. É a etapa 2 da seção 4.4.
5. **Conclusão**: documento passa a `concluido`, a pendência `documento_ausente` do tipo é resolvida, pendências `documento_invalido` anteriores do mesmo tipo também, e um evento `documento_validado` é registrado.
6. **Desbloqueio e busca automática**: se o documento for certidão de óbito e o processo estiver bloqueado, o processo é desbloqueado e as CNDs são emitidas pelo `CertidaoAdapter`, gravadas como documentos de origem `busca_automatica` e processadas pelo mesmo pipeline.
7. **Diagnóstico**: `DiagnosticoService.executar` roda ao final.

Se qualquer etapa lançar exceção, o documento volta para `pendente`, `erro_processamento` recebe a mensagem, um evento `documento_erro` é criado e nada fica pela metade (rollback da transação).

`POST /processos/{id}/documentos/{doc_id}/reprocessar` roda o pipeline de novo no mesmo arquivo, gerando uma nova `versao_extracao`.

## 8. Esquemas de extração

`app/nlp/esquemas.py` define um modelo Pydantic por tipo documental. Todos os campos são `str | None`, para que o modelo de linguagem possa devolver respostas parciais. Cada campo carrega dois metadados em `json_schema_extra`:

- `categoria`: categoria da entidade (`pessoa`, `data`, `local`, `patrimonio`, `fiscal`, `registro`, `outro`), gravada em `entidade_extraida.categoria`.
- `sinonimos`: rótulos em português que costumam anteceder aquele dado no documento. O mock usa isso para ler pares "Rótulo: valor". A implementação real pode usá-los para montar o prompt.

Os campos seguem a seção 4.4 da monografia. Certidão de óbito: nome, CPF, data de nascimento, data do óbito, naturalidade, estado civil, cônjuge, cartório. CND: tipo, órgão emissor, titular, CPF, emissão, validade, resultado. Matrícula: número, cartório, descrição, área, localização, titulares, ônus. Há esquemas também para casamento, nascimento, identidade, extrato, CRLV, IRPF, CENSEC e um genérico.

## 9. Adaptadores de integração

### LLMAdapter (contrato)

```python
class LLMAdapter(Protocol):
    nome_modelo: str
    def classificar(self, texto: str, tipo_esperado: TipoDocumento) -> ResultadoClassificacao: ...
    def extrair(self, texto: str, tipo: TipoDocumento, esquema: type[BaseModel]) -> ResultadoExtracao: ...
```

`ResultadoClassificacao` traz `tipo`, `confianca` e `justificativa`. `ResultadoExtracao` traz `dados` (dicionário com as chaves do esquema), `confianca` e `modelo`.

### MockLLMAdapter

Implementação determinística, sem rede:

- Classificação por palavras-chave com pesos, comparadas com o texto sem acentos e em minúsculas, usando fronteira de palavra. Empate é resolvido em favor do tipo esperado. Nenhuma palavra reconhecida resulta em `outro` com confiança 0,2.
- Extração lendo linhas no formato `Rótulo: valor` e casando o rótulo com os sinônimos de cada campo. Campos com `cpf` no nome recebem o primeiro CPF encontrado por regex como último recurso. A confiança é a fração de campos preenchidos.

Ele existe para o fluxo funcionar de ponta a ponta durante o desenvolvimento e para os testes serem reproduzíveis. Os PDFs gerados por `scripts/gerar_pdfs_exemplo.py` seguem esse formato.

### OpenAILLMAdapter

Esqueleto com a assinatura correta. Os dois métodos lançam `NotImplementedError` com uma mensagem orientando a implementação. É o único arquivo que o módulo de IA precisa preencher, usando LangChain e os esquemas Pydantic de `app/nlp/esquemas.py`. Depois, basta `LLM_PROVIDER=openai` no `.env`; nenhuma outra linha do backend muda.

### CertidaoAdapter

Contrato `emitir(tipo, nome, cpf, domicilio) -> ResultadoCertidao`. O `MockCertidaoAdapter` gera um PDF fictício de certidão negativa para cada esfera. O adaptador real deve consultar os portais públicos que não exigem autenticação, conforme a seção 3.3.

## 10. Diagnóstico

`DiagnosticoService.executar` implementa a seção 4.5. Ele lê as entidades da última versão de cada documento validado e aplica regras determinísticas. Cada regra produz um par (título, descrição). Ao final, `_sincronizar_pendencias` compara com as inconsistências abertas: as que deixaram de ocorrer são resolvidas com evento `pendencia_resolvida`, as novas são criadas com evento `inconsistencia_detectada`, as repetidas têm a descrição atualizada. Assim uma correção no cadastro ou um reenvio de documento faz o alerta sumir sozinho.

Regras implementadas:

| Documento | Verificação |
|---|---|
| Certidão de óbito | CPF, nome e data do óbito diferentes do cadastro; estado civil "casado" sem cônjuge cadastrado; nome do cônjuge diferente do cadastrado. Se o cadastro não tinha data do óbito, ela é preenchida a partir da certidão. |
| CND | resultado positivo (débitos); CPF diferente do de cujus; certidão vencida. |
| Matrícula | de cujus não aparece entre os titulares; matrícula recebida sem bem imóvel declarado com o mesmo identificador; ônus registrado. |
| IRPF | doações em vida informadas (possível colação, art. 2.002 do Código Civil); declaração de outro CPF. |
| CENSEC | existência de testamento. |
| Casamento | preenche `regime_bens` se estava vazio; acusa divergência se estava preenchido com outro regime. |
| Nascimento | certidão sem herdeiro correspondente; herdeiro cuja certidão não cita o de cujus como pai ou mãe. Quando bate, o herdeiro passa a `concluido`. |
| Identidade | CPF do documento diferente do cadastrado para o herdeiro. Quando bate, o herdeiro passa a `concluido`. |
| Prazo | processo ainda bloqueado mais de 60 dias após o óbito (art. 611 do CPC). |

Comparações de nome ignoram acentos, caixa e espaços; comparações de CPF usam só dígitos; datas aceitam `dd/mm/aaaa` e `aaaa-mm-dd`.

`DiagnosticoService.recomendacao` monta o texto da "próxima providência" a partir das pendências abertas, nesta ordem: bloqueante, documentos rejeitados, inconsistências, documentos obrigatórios ausentes.

## 11. Árvore genealógica

`DiagnosticoService.arvore_genealogica` devolve uma estrutura pronta para renderização: de cujus, lista de cônjuges, lista de herdeiros diretos e, dentro de cada herdeiro, seus representantes (recursivo). Herdeiros com `representa_herdeiro_id` não aparecem no primeiro nível. As observações são geradas a partir dos dados: quantos herdeiros tiveram a filiação confirmada por documento, pré-mortos com ou sem representantes, regime de bens confirmado ou pendente, ausência de inconsistências abertas.

## 12. Resumo, checklist e análise

- `GET /processos/{id}/resumo`: fase legível (`Aguardando certidão de óbito`, `Instrução documental`, `Pronto para partilha`), percentual do checklist, contadores, patrimônio total, última movimentação, pendências por módulo (documentação, herdeiros, patrimônio, árvore, análise) e os últimos eventos. É o payload único da Central.
- `GET /processos/{id}/checklist`: para cada item do catálogo, o status derivado dos documentos daquele tipo (`concluido` > `em_analise` > `pendente` > `rejeitado` > `nao_iniciado`), mais link do portal e tutorial.
- `GET /processos/{id}/analise`: contadores, uma linha por documento com o resultado do pipeline, uma linha por inconsistência aberta e a recomendação. `POST /processos/{id}/analise/executar` roda o diagnóstico sob demanda.

## 13. Autenticação e autorização

- `POST /auth/login` com e-mail e senha devolve um JWT (HS256) com validade configurável.
- Todas as rotas de processo exigem `Authorization: Bearer <token>`.
- Um processo pertence ao usuário que o criou (`responsavel_id`). A listagem só mostra os processos do usuário e o acesso a processo de outro usuário devolve 403.
- `POST /auth/usuarios` cria usuários e é restrito ao papel `administrador`.

## 14. Endpoints

| Método e rota | Função |
|---|---|
| `POST /auth/login`, `GET /auth/me`, `POST /auth/usuarios` | autenticação |
| `GET /catalogo/documentos` | catálogo documental (público) |
| `GET, POST /processos` | listar e criar (com herdeiros e bens iniciais) |
| `GET, PATCH, DELETE /processos/{id}` | detalhe, atualização parcial, remoção |
| `GET /processos/{id}/resumo`, `/checklist`, `/eventos` | Central e checklist |
| `GET, POST /processos/{id}/documentos` | listar e enviar (multipart: `tipo`, `arquivo`); o envio responde 202 e processa em segundo plano |
| `POST /processos/{id}/documentos/busca-automatica` | emitir CNDs via adaptador |
| `GET /processos/{id}/documentos/{doc}` | detalhe com texto extraído e entidades |
| `GET /processos/{id}/documentos/{doc}/arquivo` | download do PDF |
| `POST /processos/{id}/documentos/{doc}/reprocessar`, `DELETE ...` | reprocessar e remover |
| `GET, POST /processos/{id}/herdeiros`, `GET, PATCH, DELETE .../{hid}` | herdeiros |
| `GET, POST /processos/{id}/bens`, `GET, PATCH, DELETE .../{bid}` | bens |
| `GET /processos/{id}/pendencias?apenas_abertas=`, `POST .../{pid}/resolver` | pendências (bloqueantes não podem ser resolvidas à mão) |
| `GET /processos/{id}/analise`, `POST /processos/{id}/analise/executar`, `GET /processos/{id}/arvore` | diagnóstico e árvore |

Erros de domínio (`NaoEncontrado` 404, `AcessoNegado` 403, `RegraDeNegocio` 422) são convertidos em JSON `{"detail": "..."}` por um handler global.

## 15. Banco de dados e migrações

- Em desenvolvimento, `main.py` executa `create_all` na inicialização, então o SQLite funciona sem passo extra.
- Para PostgreSQL ou para evoluir o esquema, use Alembic: `alembic upgrade head` aplica a revisão inicial; `alembic revision --autogenerate -m "descricao"` gera novas revisões a partir dos modelos. O `env.py` lê `DATABASE_URL` da configuração e usa `render_as_batch` para o SQLite aceitar alterações de coluna.

## 16. Seed e PDFs de exemplo

`scripts/gerar_pdfs_exemplo.py` produz onze PDFs fictícios (certidões, matrículas, IRPF, extrato, CENSEC, RG) para o espólio de Roberto Mendes da Silva, o mesmo caso do protótipo de telas. `scripts/seed.py` cria a advogada Ana Beatriz Ramos, o inventário com quatro herdeiros e cinco bens, e envia oito documentos pelo pipeline. O resultado reproduz o cenário do protótipo: processo desbloqueado, três CNDs emitidas automaticamente, um documento rejeitado (uma certidão de nascimento enviada no lugar do RG), duas inconsistências abertas (imóvel de matrícula 78.910 não declarado e doação em vida a um herdeiro) e uma recomendação. `python scripts/seed.py --reset` apaga e recria o banco.

## 17. Testes

`tests/test_api.py` cobre, com SQLite temporário e o adaptador mock: login inválido, rota sem token, catálogo, o fluxo completo (criação bloqueada, upload de tipo errado rejeitado, certidão de óbito com CPF divergente validada e gerando inconsistência, desbloqueio, três CNDs automáticas, matrícula sem bem declarado, colação, regime de bens preenchido, herdeiro confirmado, análise, árvore, resumo, checklist), direito de representação na árvore e valor monetário formatado no cadastro de bem. Rode com `python -m pytest` dentro de `backend/`.

## 18. Decisões que divergem ou complementam a monografia

- **SQLite como padrão local**: o PostgreSQL continua sendo o banco alvo (docker-compose incluído), mas o SQLite permite qualquer integrante rodar o projeto sem Docker. O código é idêntico para os dois.
- **Tabelas de apoio** (`usuario`, `bem`, `evento`) e campos extras descritos na seção 4 deste documento. Nenhuma das cinco tabelas principais perdeu campo.
- **Inconsistências como pendências**: o diagnóstico grava alertas na tabela `pendencia` com `categoria = inconsistencia`, em vez de criar uma tabela própria. O texto da monografia já trata alertas como pendências.
- **Auto-relacionamento em herdeiro** para direito de representação.
- **Processamento assíncrono com `BackgroundTasks`** em vez de fila externa: suficiente para o escopo e sem infraestrutura adicional.
- **OCR opcional**: o Tesseract é usado se estiver instalado; caso contrário o sistema continua funcionando com PDFs nativos.
- **Adaptador de LLM em mock**: a monografia prevê GPT-4o via LangChain; o contrato está pronto e o provedor é trocado por variável de ambiente.
