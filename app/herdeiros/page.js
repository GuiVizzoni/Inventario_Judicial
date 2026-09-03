'use client'

import { useState } from 'react'
import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import Selo from '@/components/Selo'
import SemProcesso from '@/components/SemProcesso'
import { Alerta, BotaoPrimario, Campo, Selecao } from '@/components/Campo'
import { useSessao } from '@/components/SessaoProvider'
import { useDados } from '@/lib/useDados'
import { herdeiros as apiHerdeiros } from '@/lib/api'
import { iniciais } from '@/lib/formatadores'

const NOVO = { nome: '', cpf: '', parentesco: '', conjuge: false, pre_morto: false, representa_herdeiro_id: '' }

export default function Herdeiros() {
  const { processoId, carregando: carregandoSessao } = useSessao()
  const { dados: lista, erro, recarregar } = useDados(
    () => (processoId ? apiHerdeiros.listar(processoId) : Promise.resolve([])),
    [processoId]
  )
  const [mostrarForm, setMostrarForm] = useState(false)
  const [form, setForm] = useState({ ...NOVO })
  const [erroAcao, setErroAcao] = useState(null)
  const [ocupado, setOcupado] = useState(false)
  const [detalhe, setDetalhe] = useState(null)

  async function salvar(e) {
    e.preventDefault()
    setOcupado(true)
    setErroAcao(null)
    try {
      await apiHerdeiros.criar(processoId, {
        nome: form.nome,
        cpf: form.cpf || null,
        parentesco: form.parentesco,
        conjuge: form.conjuge,
        pre_morto: form.pre_morto,
        representa_herdeiro_id: form.representa_herdeiro_id || null,
      })
      setForm({ ...NOVO })
      setMostrarForm(false)
      await recarregar()
    } catch (err) {
      setErroAcao(err.message)
    } finally {
      setOcupado(false)
    }
  }

  async function remover(h) {
    if (!window.confirm(`Remover ${h.nome}?`)) return
    try {
      await apiHerdeiros.remover(processoId, h.id)
      setDetalhe(null)
      await recarregar()
    } catch (err) {
      setErroAcao(err.message)
    }
  }

  const preMortos = (lista || []).filter((h) => h.pre_morto)
  const opcoesRepresentacao = [{ valor: '', rotulo: 'Nenhum (herdeiro direto)' }].concat(preMortos.map((h) => ({ valor: h.id, rotulo: `Representa ${h.nome}` })))
  const porId = Object.fromEntries((lista || []).map((h) => [h.id, h]))

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">Sucessão</p>
            <h1 className="mt-1 font-display text-3xl font-semibold text-ink">Gestão de Herdeiros</h1>
            <p className="mt-2 text-sm text-slate">Consulte e atualize os dados sucessórios cadastrados no processo.</p>
          </div>
          {processoId && (
            <button type="button" onClick={() => setMostrarForm((v) => !v)} className="rounded-sm bg-ink px-4 py-2.5 text-sm font-medium text-parchment hover:bg-ink-soft">
              + Cadastrar herdeiro
            </button>
          )}
        </div>

        <div className="mt-6">
          <Alerta mensagem={erro || erroAcao} />
        </div>

        {!carregandoSessao && !processoId && <SemProcesso />}

        {mostrarForm && processoId && (
          <Card className="mt-6" title="Novo herdeiro">
            <form onSubmit={salvar} className="grid gap-5 sm:grid-cols-2">
              <Campo label="Nome completo" valor={form.nome} aoMudar={(v) => setForm({ ...form, nome: v })} obrigatorio />
              <Campo label="CPF" valor={form.cpf} aoMudar={(v) => setForm({ ...form, cpf: v })} placeholder="000.000.000-00" />
              <Campo label="Grau de parentesco" valor={form.parentesco} aoMudar={(v) => setForm({ ...form, parentesco: v })} placeholder="Filho(a), cônjuge, neto(a)…" obrigatorio />
              <Selecao label="Direito de representação" valor={form.representa_herdeiro_id} aoMudar={(v) => setForm({ ...form, representa_herdeiro_id: v })} opcoes={opcoesRepresentacao} />
              <label className="flex items-center gap-2 text-sm text-slate">
                <input type="checkbox" checked={form.conjuge} onChange={(e) => setForm({ ...form, conjuge: e.target.checked })} className="h-4 w-4" />
                Cônjuge ou companheiro(a) sobrevivente
              </label>
              <label className="flex items-center gap-2 text-sm text-slate">
                <input type="checkbox" checked={form.pre_morto} onChange={(e) => setForm({ ...form, pre_morto: e.target.checked })} className="h-4 w-4" />
                Herdeiro pré-morto (falecido antes do de cujus)
              </label>
              <div className="sm:col-span-2">
                <BotaoPrimario carregando={ocupado}>{ocupado ? 'Salvando…' : 'Salvar herdeiro'}</BotaoPrimario>
              </div>
            </form>
          </Card>
        )}

        {processoId && lista && lista.length === 0 && (
          <Card className="mt-8">
            <p className="text-sm text-slate">Nenhum herdeiro cadastrado.</p>
          </Card>
        )}

        {lista && lista.length > 0 && (
          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            {lista.map((h) => (
              <Card key={h.id}>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-11 w-11 items-center justify-center rounded-full bg-ink/5 font-display text-sm text-ink">
                      {iniciais(h.nome)}
                    </div>
                    <div>
                      <p className="font-medium text-ink">{h.nome}</p>
                      <p className="text-xs text-slate">
                        {h.parentesco}
                        {h.pre_morto ? ' · pré-morto' : ''}
                        {h.representa_herdeiro_id && porId[h.representa_herdeiro_id] ? ` · representa ${porId[h.representa_herdeiro_id].nome}` : ''}
                      </p>
                    </div>
                  </div>
                  <Selo status={h.status} />
                </div>
                <div className="mt-4 flex items-center justify-between border-t border-ink/10 pt-3 text-xs">
                  <span className="font-mono text-slate">{h.cpf || 'CPF não informado'}</span>
                  <div className="flex gap-3">
                    <button type="button" onClick={() => setDetalhe(detalhe && detalhe.id === h.id ? null : h)} className="text-bronze-dark hover:underline">
                      {detalhe && detalhe.id === h.id ? 'Ocultar' : 'Ver detalhes'}
                    </button>
                    <button type="button" onClick={() => remover(h)} className="text-selo-danger hover:underline">
                      Remover
                    </button>
                  </div>
                </div>
                {detalhe && detalhe.id === h.id && (
                  <dl className="mt-3 grid grid-cols-2 gap-y-1 border-t border-ink/10 pt-3 text-xs">
                    <dt className="text-slate">Cônjuge</dt>
                    <dd className="text-ink">{h.conjuge ? 'Sim' : 'Não'}</dd>
                    <dt className="text-slate">Pré-morto</dt>
                    <dd className="text-ink">{h.pre_morto ? 'Sim' : 'Não'}</dd>
                    <dt className="text-slate">Situação</dt>
                    <dd className="text-ink">
                      {h.status === 'concluido' ? 'Vínculo confirmado por documento' : h.status === 'rejeitado' ? 'Documento rejeitado' : 'Aguardando certidão ou documento de identidade'}
                    </dd>
                  </dl>
                )}
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
