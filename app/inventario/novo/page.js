'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import { Alerta, Campo, Selecao } from '@/components/Campo'
import { useSessao } from '@/components/SessaoProvider'
import { documentos as apiDocumentos, processos as apiProcessos } from '@/lib/api'
import { CATEGORIAS_BEM } from '@/lib/formatadores'

const ETAPAS = ['Falecido (de cujus)', 'Herdeiros conhecidos', 'Bens conhecidos']

const HERDEIRO_VAZIO = { nome: '', parentesco: '', cpf: '' }
const BEM_VAZIO = { descricao: '', categoria: 'imovel', valor_estimado: '', identificador: '' }

export default function NovoInventario() {
  const router = useRouter()
  const { escolherProcesso, carregarProcessos } = useSessao()
  const [etapa, setEtapa] = useState(0)
  const [deCujus, setDeCujus] = useState({ nome_de_cujus: '', cpf_de_cujus: '', data_obito: '', ultimo_domicilio: '', numero_processo: '' })
  const [certidao, setCertidao] = useState(null)
  const [herdeiros, setHerdeiros] = useState([{ ...HERDEIRO_VAZIO }, { ...HERDEIRO_VAZIO }])
  const [bens, setBens] = useState([{ ...BEM_VAZIO }])
  const [erro, setErro] = useState(null)
  const [salvando, setSalvando] = useState(false)

  function atualizarLista(setter, indice, campo, valor) {
    setter((lista) => lista.map((item, i) => (i === indice ? { ...item, [campo]: valor } : item)))
  }

  function removerDaLista(setter, indice) {
    setter((lista) => lista.filter((_, i) => i !== indice))
  }

  function validarEtapa() {
    if (etapa === 0) {
      if (!deCujus.nome_de_cujus.trim() || !deCujus.cpf_de_cujus.trim()) {
        setErro('Informe o nome e o CPF do de cujus.')
        return false
      }
    }
    setErro(null)
    return true
  }

  async function concluir() {
    if (!validarEtapa()) return
    setSalvando(true)
    setErro(null)
    try {
      const dados = {
        ...deCujus,
        data_obito: deCujus.data_obito || null,
        ultimo_domicilio: deCujus.ultimo_domicilio || null,
        numero_processo: deCujus.numero_processo || null,
        herdeiros: herdeiros
          .filter((h) => h.nome.trim() && h.parentesco.trim())
          .map((h) => ({ nome: h.nome.trim(), parentesco: h.parentesco.trim(), cpf: h.cpf || null })),
        bens: bens
          .filter((b) => b.descricao.trim())
          .map((b) => ({ descricao: b.descricao.trim(), categoria: b.categoria, valor_estimado: b.valor_estimado || '0', identificador: b.identificador || null })),
      }
      const processo = await apiProcessos.criar(dados)
      if (certidao) {
        await apiDocumentos.enviar(processo.id, 'certidao_obito', certidao)
      }
      await carregarProcessos(processo.id)
      escolherProcesso(processo.id)
      router.push('/central')
    } catch (e) {
      setErro(e.message)
      setSalvando(false)
    }
  }

  function avancar() {
    if (!validarEtapa()) return
    if (etapa === ETAPAS.length - 1) concluir()
    else setEtapa((e) => e + 1)
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-3xl px-6 py-10">
        <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">Novo processo</p>
        <h1 className="mt-1 font-display text-3xl font-semibold text-ink">Cadastro Inicial do Inventário</h1>
        <p className="mt-2 text-sm text-slate">
          Registre os dados básicos do de cujus, dos herdeiros e dos bens conhecidos
          para abrir o procedimento sucessório. A certidão de óbito é obrigatória para
          desbloquear o protocolo.
        </p>

        <ol className="mt-8 flex items-center gap-2">
          {ETAPAS.map((nome, i) => (
            <li key={nome} className="flex flex-1 items-center gap-2">
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full font-mono text-xs ${
                  i <= etapa ? 'bg-ink text-parchment' : 'bg-ink/10 text-slate'
                }`}
              >
                {i + 1}
              </div>
              <span className={`hidden text-sm sm:block ${i === etapa ? 'text-ink' : 'text-slate'}`}>{nome}</span>
              {i < ETAPAS.length - 1 && <div className="h-px flex-1 bg-ink/10" />}
            </li>
          ))}
        </ol>

        <Card className="mt-8">
          {etapa === 0 && (
            <div className="space-y-5">
              <h3 className="font-display text-lg font-semibold text-ink">Dados do de cujus</h3>
              <Campo label="Nome completo" valor={deCujus.nome_de_cujus} aoMudar={(v) => setDeCujus({ ...deCujus, nome_de_cujus: v })} placeholder="Roberto Mendes da Silva" obrigatorio />
              <div className="grid gap-5 sm:grid-cols-2">
                <Campo label="CPF" valor={deCujus.cpf_de_cujus} aoMudar={(v) => setDeCujus({ ...deCujus, cpf_de_cujus: v })} placeholder="000.000.000-00" obrigatorio />
                <Campo label="Data do falecimento" tipo="date" valor={deCujus.data_obito} aoMudar={(v) => setDeCujus({ ...deCujus, data_obito: v })} />
              </div>
              <div className="grid gap-5 sm:grid-cols-2">
                <Campo label="Último domicílio" valor={deCujus.ultimo_domicilio} aoMudar={(v) => setDeCujus({ ...deCujus, ultimo_domicilio: v })} placeholder="Cidade / Estado" />
                <Campo label="Número do processo (se distribuído)" valor={deCujus.numero_processo} aoMudar={(v) => setDeCujus({ ...deCujus, numero_processo: v })} placeholder="0000000-00.0000.0.00.0000" />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-ink">Certidão de óbito (PDF)</label>
                <label className="block cursor-pointer rounded-sm border-2 border-dashed border-ink/15 px-4 py-6 text-center text-sm text-slate hover:border-bronze/60">
                  {certidao ? (
                    <span className="text-ink">{certidao.name}</span>
                  ) : (
                    <>
                      Arraste o arquivo ou <span className="text-bronze-dark">selecione no computador</span>
                    </>
                  )}
                  <input type="file" accept="application/pdf" className="hidden" onChange={(e) => setCertidao(e.target.files[0] || null)} />
                </label>
              </div>
            </div>
          )}

          {etapa === 1 && (
            <div className="space-y-5">
              <h3 className="font-display text-lg font-semibold text-ink">Herdeiros conhecidos</h3>
              {herdeiros.map((h, i) => (
                <div key={i} className="grid gap-5 rounded-sm border border-ink/10 p-4 sm:grid-cols-3">
                  <Campo label="Nome completo" valor={h.nome} aoMudar={(v) => atualizarLista(setHerdeiros, i, 'nome', v)} placeholder="Nome do herdeiro" />
                  <Campo label="Grau de parentesco" valor={h.parentesco} aoMudar={(v) => atualizarLista(setHerdeiros, i, 'parentesco', v)} placeholder="Filho(a), cônjuge…" />
                  <div className="flex items-end gap-2">
                    <Campo label="CPF" valor={h.cpf} aoMudar={(v) => atualizarLista(setHerdeiros, i, 'cpf', v)} placeholder="000.000.000-00" className="flex-1" />
                    <button type="button" onClick={() => removerDaLista(setHerdeiros, i)} className="pb-2.5 text-xs text-selo-danger hover:underline">
                      remover
                    </button>
                  </div>
                </div>
              ))}
              <button type="button" onClick={() => setHerdeiros([...herdeiros, { ...HERDEIRO_VAZIO }])} className="text-sm font-medium text-bronze-dark hover:underline">
                + Adicionar outro herdeiro
              </button>
            </div>
          )}

          {etapa === 2 && (
            <div className="space-y-5">
              <h3 className="font-display text-lg font-semibold text-ink">Bens conhecidos</h3>
              {bens.map((b, i) => (
                <div key={i} className="grid gap-5 rounded-sm border border-ink/10 p-4 sm:grid-cols-2">
                  <Campo label="Descrição do bem" valor={b.descricao} aoMudar={(v) => atualizarLista(setBens, i, 'descricao', v)} placeholder="Imóvel, veículo, conta…" />
                  <Selecao label="Categoria" valor={b.categoria} aoMudar={(v) => atualizarLista(setBens, i, 'categoria', v)} opcoes={CATEGORIAS_BEM} />
                  <Campo label="Valor estimado" valor={b.valor_estimado} aoMudar={(v) => atualizarLista(setBens, i, 'valor_estimado', v)} placeholder="R$ 0,00" />
                  <div className="flex items-end gap-2">
                    <Campo label="Identificador (matrícula, placa, conta)" valor={b.identificador} aoMudar={(v) => atualizarLista(setBens, i, 'identificador', v)} placeholder="Opcional" className="flex-1" />
                    <button type="button" onClick={() => removerDaLista(setBens, i)} className="pb-2.5 text-xs text-selo-danger hover:underline">
                      remover
                    </button>
                  </div>
                </div>
              ))}
              <button type="button" onClick={() => setBens([...bens, { ...BEM_VAZIO }])} className="text-sm font-medium text-bronze-dark hover:underline">
                + Adicionar outro bem
              </button>
            </div>
          )}

          <div className="mt-6">
            <Alerta mensagem={erro} />
          </div>

          <div className="mt-6 flex justify-between border-t border-ink/10 pt-6">
            <button
              type="button"
              onClick={() => setEtapa((e) => Math.max(0, e - 1))}
              disabled={etapa === 0 || salvando}
              className="rounded-sm px-4 py-2 text-sm font-medium text-slate hover:text-ink disabled:opacity-40"
            >
              Voltar
            </button>
            <button
              type="button"
              onClick={avancar}
              disabled={salvando}
              className="rounded-sm bg-ink px-5 py-2.5 text-sm font-medium text-parchment hover:bg-ink-soft disabled:opacity-60"
            >
              {salvando ? 'Salvando…' : etapa === ETAPAS.length - 1 ? 'Concluir cadastro' : 'Próxima etapa'}
            </button>
          </div>
        </Card>
      </main>
    </div>
  )
}
