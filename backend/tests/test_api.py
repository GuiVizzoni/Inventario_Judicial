from scripts.gerar_pdfs_exemplo import EXEMPLOS

PROCESSO = {
    "nome_de_cujus": "Roberto Mendes da Silva",
    "cpf_de_cujus": "321.654.987-00",
    "data_obito": "2026-07-10",
    "ultimo_domicilio": "São Paulo/SP",
    "herdeiros": [
        {"nome": "Carlos Mendes da Silva", "cpf": "123.456.789-00", "parentesco": "Filho"},
        {"nome": "Juliana Mendes Ribeiro", "cpf": "234.567.890-11", "parentesco": "Filha"},
        {"nome": "Marta Aparecida Silva", "cpf": "345.678.901-22", "parentesco": "Cônjuge", "conjuge": True},
    ],
    "bens": [
        {"descricao": "Apartamento - Jardins", "categoria": "imovel", "valor_estimado": "1250000.00", "identificador": "45.678"},
        {"descricao": "Sítio - Atibaia/SP", "categoria": "imovel_rural", "valor_estimado": "620000.00"},
    ],
}


def enviar(cliente, cabecalhos, processo_id, tipo, nome):
    resposta = cliente.post(
        f"/processos/{processo_id}/documentos",
        headers=cabecalhos,
        data={"tipo": tipo},
        files={"arquivo": (nome, EXEMPLOS[nome], "application/pdf")},
    )
    assert resposta.status_code == 202, resposta.text
    return resposta.json()


def test_login_invalido(cliente):
    resposta = cliente.post("/auth/login", json={"email": "ana@teste.com", "senha": "errada"})
    assert resposta.status_code == 401


def test_rota_protegida_sem_token(cliente):
    assert cliente.get("/processos").status_code == 401


def test_catalogo_documental(cliente):
    itens = cliente.get("/catalogo/documentos").json()
    tipos = {i["tipo"] for i in itens}
    assert "certidao_obito" in tipos
    bloqueantes = [i for i in itens if i["bloqueante"]]
    assert len(bloqueantes) == 1 and bloqueantes[0]["tipo"] == "certidao_obito"


def test_fluxo_completo(cliente, cabecalhos, cabecalhos_outro):
    criado = cliente.post("/processos", headers=cabecalhos, json=PROCESSO)
    assert criado.status_code == 201, criado.text
    processo = criado.json()
    pid = processo["id"]
    assert processo["status"] == "bloqueado"

    assert cliente.get(f"/processos/{pid}", headers=cabecalhos_outro).status_code == 403

    checklist = cliente.get(f"/processos/{pid}/checklist", headers=cabecalhos).json()
    assert checklist["percentual"] == 0
    assert all(i["status"] == "nao_iniciado" for i in checklist["itens"])

    pendencias = cliente.get(f"/processos/{pid}/pendencias", headers=cabecalhos).json()
    assert any(p["bloqueante"] and p["tipo_documento"] == "certidao_obito" for p in pendencias)

    errado = enviar(cliente, cabecalhos, pid, "certidao_obito", "certidao_nascimento_juliana.pdf")
    detalhe = cliente.get(f"/processos/{pid}/documentos/{errado['id']}", headers=cabecalhos).json()
    assert detalhe["status_validacao"] == "rejeitado"
    assert detalhe["tipo_detectado"] == "certidao_nascimento"
    assert cliente.get(f"/processos/{pid}", headers=cabecalhos).json()["status"] == "bloqueado"

    obito = enviar(cliente, cabecalhos, pid, "certidao_obito", "certidao_obito_cpf_divergente.pdf")
    detalhe = cliente.get(f"/processos/{pid}/documentos/{obito['id']}", headers=cabecalhos).json()
    assert detalhe["status_validacao"] == "concluido", detalhe
    chaves = {e["chave"]: e["valor"] for e in detalhe["entidades"]}
    assert chaves["cpf"] == "999.888.777-66"
    assert chaves["data_obito"] == "10/07/2026"
    assert detalhe["texto_extraido"]

    processo = cliente.get(f"/processos/{pid}", headers=cabecalhos).json()
    assert processo["status"] == "aberto"
    assert processo["data_abertura"] is not None

    documentos = cliente.get(f"/processos/{pid}/documentos", headers=cabecalhos).json()
    automaticos = [d for d in documentos if d["origem"] == "busca_automatica"]
    assert len(automaticos) == 3
    assert all(d["status_validacao"] == "concluido" for d in automaticos)

    pendencias = cliente.get(f"/processos/{pid}/pendencias", headers=cabecalhos).json()
    titulos = {p["titulo"] for p in pendencias}
    assert "CPF do de cujus divergente" in titulos
    assert not any(p["bloqueante"] for p in pendencias)

    enviar(cliente, cabecalhos, pid, "certidao_matricula", "matricula_sitio_atibaia.pdf")
    enviar(cliente, cabecalhos, pid, "declaracao_irpf", "irpf_2025_roberto.pdf")
    enviar(cliente, cabecalhos, pid, "certidao_nascimento", "certidao_nascimento_juliana.pdf")
    enviar(cliente, cabecalhos, pid, "certidao_casamento", "certidao_casamento.pdf")

    pendencias = cliente.get(f"/processos/{pid}/pendencias", headers=cabecalhos).json()
    titulos = {p["titulo"] for p in pendencias}
    assert "Imóvel não declarado no patrimônio" in titulos
    assert "Possível necessidade de colação" in titulos

    processo = cliente.get(f"/processos/{pid}", headers=cabecalhos).json()
    assert processo["regime_bens"] == "Comunhão parcial de bens"

    herdeiros = cliente.get(f"/processos/{pid}/herdeiros", headers=cabecalhos).json()
    juliana = next(h for h in herdeiros if h["nome"] == "Juliana Mendes Ribeiro")
    assert juliana["status"] == "concluido"

    analise = cliente.get(f"/processos/{pid}/analise", headers=cabecalhos).json()
    assert analise["itens_analisados"] > 0
    assert analise["inconsistencias"] >= 3
    assert "recomenda" in analise["recomendacao"].lower()

    arvore = cliente.get(f"/processos/{pid}/arvore", headers=cabecalhos).json()
    assert arvore["de_cujus"]["nome"] == "Roberto Mendes da Silva"
    assert len(arvore["conjuges"]) == 1
    assert len(arvore["herdeiros"]) == 2

    resumo = cliente.get(f"/processos/{pid}/resumo", headers=cabecalhos).json()
    assert resumo["fase"] == "Instrução documental"
    assert resumo["progresso_documental"] > 0
    assert resumo["herdeiros_cadastrados"] == 3
    assert resumo["atividades"]

    checklist = cliente.get(f"/processos/{pid}/checklist", headers=cabecalhos).json()
    por_tipo = {i["tipo"]: i["status"] for i in checklist["itens"]}
    assert por_tipo["certidao_obito"] == "concluido"
    assert por_tipo["cnd_federal"] == "concluido"
    assert por_tipo["certidao_censec"] == "nao_iniciado"


def test_representacao_na_arvore(cliente, cabecalhos):
    pid = cliente.post("/processos", headers=cabecalhos, json={"nome_de_cujus": "Maria Souza", "cpf_de_cujus": "111.222.333-44"}).json()["id"]
    pai = cliente.post(f"/processos/{pid}/herdeiros", headers=cabecalhos, json={"nome": "João Souza", "parentesco": "Filho", "pre_morto": True}).json()
    neto = cliente.post(f"/processos/{pid}/herdeiros", headers=cabecalhos, json={"nome": "Lucas Souza", "parentesco": "Neto", "representa_herdeiro_id": pai["id"]})
    assert neto.status_code == 201, neto.text
    arvore = cliente.get(f"/processos/{pid}/arvore", headers=cabecalhos).json()
    assert arvore["herdeiros"][0]["pre_morto"] is True
    assert arvore["herdeiros"][0]["representantes"][0]["nome"] == "Lucas Souza"
    assert any("1.851" in o for o in arvore["observacoes"])

    auto = cliente.post(f"/processos/{pid}/documentos/busca-automatica", headers=cabecalhos)
    assert auto.status_code == 422


def test_bem_com_valor_formatado(cliente, cabecalhos):
    pid = cliente.post("/processos", headers=cabecalhos, json={"nome_de_cujus": "José Lima", "cpf_de_cujus": "555.666.777-88"}).json()["id"]
    bem = cliente.post(f"/processos/{pid}/bens", headers=cabecalhos, json={"descricao": "Carro", "categoria": "movel", "valor_estimado": "R$ 118.000,00"})
    assert bem.status_code == 201, bem.text
    assert bem.json()["valor_estimado"] == "118000.00"
