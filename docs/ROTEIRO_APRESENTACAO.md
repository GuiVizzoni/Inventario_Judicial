# Roteiro de apresentação

Tempo estimado: 15 a 20 minutos. A ideia é mostrar o fluxo da Figura 1 da monografia acontecendo ao vivo: formulário → certidão de óbito bloqueante → busca automática → upload assistido → camada de IA → painel.

## 0. Preparação (antes de começar, com calma)

Abra três terminais.

Terminal 1, backend:

```bash
cd backend
.venv\Scripts\activate
python scripts/seed.py --reset
python scripts/gerar_pdfs_exemplo.py
uvicorn app.main:app --reload --port 8000
```

Terminal 2, frontend:

```bash
npm run dev
```

Terminal 3, livre para rodar os testes no final.

Deixe abertas no navegador, em abas separadas:

- `http://localhost:3000/login`
- `http://localhost:8000/docs` (Swagger)
- a pasta `backend/exemplos/` no explorador de arquivos, para arrastar os PDFs

Deixe abertos no editor, para mostrar rapidamente:

- `backend/app/services/documento_service.py` (pipeline)
- `backend/app/integrations/llm_openai.py` (ponto de encaixe da IA)
- `backend/app/nlp/esquemas.py` (esquemas de extração)

O seed cria um inventário já completo (Roberto Mendes da Silva). Ele é o seu plano B: se algo falhar ao vivo, troque para ele no seletor da Central e mostre o resultado final.

Credenciais: `ana.ramos@escritorio.com.br` / `inventario123`.

## 1. Contexto e arquitetura (2 min, sem clicar)

Fale, com o editor aberto na pasta `backend/app`:

- Monolito modular em quatro camadas, como na seção 4.2: `api/` → `services/` → `integrations/` e `repositories/`.
- Os quatro serviços da monografia existem com o mesmo nome: `ProcessoService`, `DocumentoService`, `NLPService`, `DiagnosticoService`.
- Os dois adaptadores também: `LLMAdapter` e `CertidaoAdapter`.
- Banco: as cinco tabelas do diagrama mais `usuario`, `bem` e `evento` de apoio.
- Frase-chave: "a IA é um adaptador trocável por variável de ambiente; hoje roda um mock heurístico, e o módulo de IA vai entregar a implementação com GPT-4o e LangChain sem mudar nenhuma outra linha".

## 2. Login e Central (1 min)

1. Faça login.
2. Na Central, mostre o seletor de processo (há um inventário pronto do seed). Diga que vai criar outro do zero para mostrar o fluxo inteiro.

## 3. Cadastro inicial: o protocolo nasce bloqueado (2 min)

1. Clique em **+ Novo inventário**.
2. Etapa 1, preencha exatamente (os PDFs de exemplo usam estes dados):
   - Nome: `Roberto Mendes da Silva`
   - CPF: `321.654.987-00`
   - Data do falecimento: `10/07/2026`
   - Último domicílio: `São Paulo/SP`
   - **Não anexe a certidão de óbito agora.** É proposital.
3. Etapa 2, herdeiros:
   - `Carlos Mendes da Silva`, `Filho`, CPF `123.456.789-00`
   - `Juliana Mendes Ribeiro`, `Filha`, CPF `234.567.890-11`
   - `Marta Aparecida Silva`, `Cônjuge`, CPF `345.678.901-22`
4. Etapa 3, bens:
   - `Apartamento - Jardins, São Paulo/SP`, Imóvel, `1250000`, identificador `45.678`
   - `Veículo Honda Civic 2022`, Móvel, `118000`
5. Concluir cadastro. Volta para a Central.

O que apontar:

- Selo vermelho **Protocolo bloqueado** e fase **Aguardando certidão de óbito**.
- Progresso documental 0%.
- Abra **Documentação → Ver checklist**: todos os itens "não iniciado", a certidão de óbito marcada como *bloqueante*, os outros como obrigatório ou complementar, cada um com o tutorial e o link do portal (isso é a estratégia de links dinâmicos da seção 3.3).
- Volte em **Documentação** e passe o mouse sobre **Buscar certidões negativas**: o botão está desabilitado e a dica diz que a busca só fica disponível após a validação da certidão de óbito. A API também recusa a chamada direta (HTTP 422). É a regra do art. 611 implementada.
- Abra **Análise IA**: a recomendação pede a certidão de óbito.

## 4. Validação de tipo: o arquivo errado é rejeitado (2 min)

1. Em **Documentação → + Enviar documento**, escolha tipo **Certidão de óbito** e envie o arquivo `certidao_nascimento_juliana.pdf` (de propósito).
2. Clique em **Atualizar** após um ou dois segundos.
3. O documento aparece **Rejeitado**. Clique no nome do arquivo: o painel de detalhe mostra o motivo ("enviado como certidão de óbito, mas o conteúdo corresponde a certidão de nascimento"), o texto extraído e o método de extração.
4. Mostre que o processo continua bloqueado na Central.

Isso é a etapa 1 do pipeline da seção 4.4: classificação antes da extração, evitando que um anexo errado trave o processo.

## 5. Certidão de óbito: desbloqueio e busca automática (3 min)

1. Envie `certidao_obito_roberto.pdf` como **Certidão de óbito**. Clique em **Atualizar**.
2. Apontar, na mesma tela:
   - a certidão ficou **Concluído**;
   - apareceram três novos documentos com a marca *busca automática* (CND federal, estadual e municipal), também concluídos. Foram emitidos pelo `CertidaoAdapter` e passaram pelo mesmo pipeline;
   - a pendência "rejeitada" da certidão de óbito foi resolvida sozinha.
3. Clique na certidão de óbito e mostre as **entidades extraídas**: nome, CPF, datas, estado civil, cônjuge, cartório, com o nome do modelo, a versão da extração e a confiança. Diga que isso é a tabela `ENTIDADE_EXTRAIDA`, separada de `DOCUMENTO` para permitir reprocessar com outro modelo sem perder o original.
4. Volte à Central: fase mudou para **Instrução documental**, selo mudou, progresso subiu, "atividade recente" mostra a sequência de eventos (recebida → validada → desbloqueado → CNDs).
5. Abra o checklist: 4 de 12 concluídos.

## 6. Diagnóstico: cruzando documentos com o formulário (4 min)

Três envios curtos, cada um gera um tipo diferente de inconsistência.

**a) Imóvel não declarado**

1. Envie `matricula_sitio_atibaia.pdf` como **Certidão de matrícula**.
2. Abra **Análise IA**: aparece "Imóvel não declarado no patrimônio" (a matrícula 78.910 foi recebida, mas não há bem com esse identificador).
3. Vá em **Patrimônio → + Declarar bem**: `Sítio - Atibaia/SP`, Imóvel rural, `620000`, identificador `78.910`.
4. Volte em **Análise IA** e clique em **Executar nova análise**: a inconsistência some sozinha. Frase: "o diagnóstico é sincronizado, não acumula alertas velhos".

**b) Colação**

1. Envie `irpf_2025_roberto.pdf` como **Declaração de Imposto de Renda**.
2. Análise IA mostra "Possível necessidade de colação", citando a doação em vida a Pedro Henrique e o art. 2.002 do Código Civil. Esse é o exemplo central da seção 4.5.

**c) Confirmação de herdeiro e regime de bens**

1. Envie `certidao_casamento.pdf` como **Certidão de casamento** e `certidao_nascimento_juliana.pdf` como **Certidão de nascimento dos herdeiros**.
2. Em **Herdeiros**, Juliana passou a **Concluído** (filiação confirmada pela certidão, que cita Roberto e Marta como pais).
3. Em **Árvore Genealógica**: Juliana aparece com a marca *confirmado*, e as observações agora dizem "1 de 2 herdeiros diretos confirmados" e "Regime de bens: Comunhão parcial de bens", lido da certidão de casamento e gravado no processo.

Se sobrar tempo: em **Herdeiros**, cadastre `Pedro Henrique Mendes`, Filho, marque **pré-morto**, depois cadastre `Lucas Mendes`, Neto, com "Representa Pedro Henrique Mendes". A árvore desenha o neto abaixo do pai riscado, e a observação cita o art. 1.851.

## 7. Divergência com o cadastro (1 min, opcional)

Troque para o inventário do seed no seletor da Central e abra **Documentação**: lá há um RG rejeitado e duas inconsistências abertas, prontos. Ou, no processo que você criou, reprocesse: envie `certidao_obito_cpf_divergente.pdf` como certidão de óbito e mostre em **Análise IA** o alerta "CPF do de cujus divergente" comparando cadastro e certidão.

## 8. A API por trás (2 min)

1. Abra `http://localhost:8000/docs`. Mostre os grupos: Autenticação, Catálogo, Processos, Documentos, Herdeiros, Patrimônio, Pendências, Diagnóstico.
2. Expanda `GET /processos/{id}/resumo` e diga que a Central inteira é um único payload.
3. Frase: "o frontend não tem mais nenhum dado fixo; tudo que apareceu veio destes endpoints".

## 9. Ponto de encaixe da IA (2 min)

No editor:

1. `backend/app/integrations/llm_adapter.py`: o contrato, dois métodos.
2. `backend/app/integrations/llm_openai.py`: o esqueleto que o módulo de IA vai preencher.
3. `backend/app/nlp/esquemas.py`: o esquema da certidão de óbito, com os campos da seção 4.4 e os sinônimos que podem virar prompt.
4. `backend/.env.example`: `LLM_PROVIDER=mock` vira `openai`.

Frase: "o TCC-II mede precisão e tempo; `documento.processamento_iniciado_em/concluido_em`, `entidade_extraida.duracao_ms` e `modelo_llm` já estão sendo gravados hoje, então a avaliação experimental não precisa de mudança de esquema".

## 10. Testes (1 min)

No terminal 3:

```bash
cd backend
.venv\Scripts\activate
python -m pytest -q
```

Seis testes passam em poucos segundos. Diga que `test_fluxo_completo` reproduz exatamente o roteiro que acabou de ser mostrado ao vivo.

## Se algo der errado

| Sintoma | O que fazer |
|---|---|
| Tela não carrega ou erro de rede | confira se o terminal 1 mostra `Uvicorn running on http://127.0.0.1:8000` |
| Documento fica "pendente" sem mudar | clique em **Atualizar**; se persistir, clique em **reprocessar** na linha |
| Sessão expirou | faça login de novo; o processo selecionado é lembrado |
| Quer recomeçar do zero | `python scripts/seed.py --reset` no terminal 1 (com o uvicorn parado) |
| Tudo falhou | use o inventário do seed no seletor da Central: ele já tem todo o cenário final |

## Ordem resumida para colar num papel

1. Login → Central → seletor.
2. Novo inventário sem certidão → bloqueado → checklist → busca automática recusada → recomendação.
3. Enviar `certidao_nascimento_juliana.pdf` como óbito → rejeitado → motivo.
4. Enviar `certidao_obito_roberto.pdf` → concluído → 3 CNDs automáticas → entidades → Central desbloqueada.
5. `matricula_sitio_atibaia.pdf` → alerta → declarar bem 78.910 → executar análise → alerta some.
6. `irpf_2025_roberto.pdf` → colação.
7. `certidao_casamento.pdf` + `certidao_nascimento_juliana.pdf` → Juliana confirmada → árvore e regime de bens.
8. Swagger → contrato do LLMAdapter → `.env` → testes.
