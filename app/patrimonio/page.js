'use client'

import { useState } from 'react'
import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import Selo from '@/components/Selo'
import SemProcesso from '@/components/SemProcesso'
import { Alerta, BotaoPrimario, Campo, Selecao } from '@/components/Campo'
import { useSessao } from '@/components/SessaoProvider'
import { useDados } from '@/lib/useDados'
import { bens as apiBens } from '@/lib/api'
import { CATEGORIAS_BEM, formatarMoeda, rotuloCategoriaBem } from '@/lib/formatadores'

const NOVO = { descricao: '', categoria: 'imovel', valor_estimado: '', identificador: '' }

export default function Patrimonio() {
  const { processoId, carregando: carregandoSessao } = useSessao()
  const { dados: lista, erro, recarregar } = useDados(
    () => (processoId ? apiBens.listar(processoId) : Promise.resolve([])),
    [processoId]
  )
  const [mostrarForm, setMostrarForm] = useState(false)
  const [form, setForm] = useState({ ...NOVO })
  const [erroAcao, setErroAcao] = useState(null)
  const [ocupado, setOcupado] = useState(false)

  async function salvar(e) {
    e.preventDefault()
    setOcupado(true)
    setErroAcao(null)
    try {
      await apiBens.criar(processoId, {
        descricao: form.descricao,
        categoria: form.categoria,
        valor_estimado: form.valor_estimado || '0',
        identificador: form.identificador || null,
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

  async function remover(b) {
    if (!window.confirm(`Remover "${b.descricao}"?`)) return
    try {
      await apiBens.remover(processoId, b.id)
      await recarregar()
    } catch (err) {
      setErroAcao(err.message)
    }
  }

  async function marcar(b, status) {
    try {
      await apiBens.atualizar(processoId, b.id, { status })
      await recarregar()
    } catch (err) {
      setErroAcao(err.message)
    }
  }

  const total = (lista || []).reduce((soma, b) => soma + Number(b.valor_estimado || 0), 0)

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">Bens</p>
            <h1 className="mt-1 font-display text-3xl font-semibold text-ink">Gestão Patrimonial</h1>
            <p className="mt-2 text-sm text-slate">Organização e acompanhamento dos bens declarados no inventário.</p>
          </div>
          {processoId && (
            <button type="button" onClick={() => setMostrarForm((v) => !v)} className="rounded-sm bg-ink px-4 py-2.5 text-sm font-medium text-parchment hover:bg-ink-soft">
              + Declarar bem
            </button>
          )}
        </div>

        <div className="mt-6">
          <Alerta mensagem={erro || erroAcao} />
        </div>

        {!carregandoSessao && !processoId && <SemProcesso />}

        {mostrarForm && processoId && (
          <Card className="mt-6" title="Novo bem">
            <form onSubmit={salvar} className="grid gap-5 sm:grid-cols-2">
              <Campo label="Descrição do bem" valor={form.descricao} aoMudar={(v) => setForm({ ...form, descricao: v })} placeholder="Apartamento, veículo, conta…" obrigatorio />
              <Selecao label="Categoria" valor={form.categoria} aoMudar={(v) => setForm({ ...form, categoria: v })} opcoes={CATEGORIAS_BEM} />
              <Campo label="Valor estimado" valor={form.valor_estimado} aoMudar={(v) => setForm({ ...form, valor_estimado: v })} placeholder="R$ 0,00" />
              <Campo label="Identificador (matrícula, placa, conta)" valor={form.identificador} aoMudar={(v) => setForm({ ...form, identificador: v })} placeholder="Usado para cruzar com os documentos" />
              <div className="sm:col-span-2">
                <BotaoPrimario carregando={ocupado}>{ocupado ? 'Salvando…' : 'Salvar bem'}</BotaoPrimario>
              </div>
            </form>
          </Card>
        )}

        {lista && (
          <>
            <Card className="mt-8" eyebrow="Patrimônio total declarado" title={formatarMoeda(total)}>
              <p className="text-sm text-slate">Soma bruta dos bens registrados, antes de partilha e deduções legais.</p>
            </Card>

            <Card className="mt-6" title="Bens declarados">
              {lista.length === 0 ? (
                <p className="text-sm text-slate">Nenhum bem declarado.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-ink/10 text-xs uppercase tracking-wide text-slate">
                        <th className="py-2 pr-4 font-medium">Descrição</th>
                        <th className="py-2 pr-4 font-medium">Categoria</th>
                        <th className="py-2 pr-4 font-medium">Valor estimado</th>
                        <th className="py-2 pr-4 font-medium">Situação</th>
                        <th className="py-2 pr-4 font-medium"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {lista.map((b) => (
                        <tr key={b.id} className="border-b border-ink/5 last:border-0">
                          <td className="py-3 pr-4 text-ink">
                            {b.descricao}
                            {b.identificador && <p className="font-mono text-[11px] text-slate">{b.identificador}</p>}
                          </td>
                          <td className="py-3 pr-4 text-slate">{rotuloCategoriaBem(b.categoria)}</td>
                          <td className="py-3 pr-4 font-mono text-xs text-ink">{formatarMoeda(b.valor_estimado)}</td>
                          <td className="py-3 pr-4">
                            <Selo status={b.status} />
                          </td>
                          <td className="py-3 pr-4 text-right text-xs">
                            {b.status !== 'concluido' && (
                              <>
                                <button type="button" onClick={() => marcar(b, 'concluido')} className="text-bronze-dark hover:underline">
                                  confirmar
                                </button>
                                <span className="text-slate"> · </span>
                              </>
                            )}
                            <button type="button" onClick={() => remover(b)} className="text-selo-danger hover:underline">
                              remover
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          </>
        )}
      </main>
    </div>
  )
}
