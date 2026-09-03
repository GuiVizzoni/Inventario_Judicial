'use client'

import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import Selo from '@/components/Selo'
import ProgressoDocumental from '@/components/ProgressoDocumental'
import SemProcesso from '@/components/SemProcesso'
import { Alerta } from '@/components/Campo'
import { useSessao } from '@/components/SessaoProvider'
import { useDados } from '@/lib/useDados'
import { processos as apiProcessos } from '@/lib/api'
import { formatarData, tempoRelativo } from '@/lib/formatadores'

const MODULOS = [
  { chave: 'documentos', titulo: 'Documentação', href: '/documentos', desc: 'Envio e checklist de documentos' },
  { chave: 'herdeiros', titulo: 'Herdeiros', href: '/herdeiros', desc: 'Cadastro e dados sucessórios' },
  { chave: 'patrimonio', titulo: 'Patrimônio', href: '/patrimonio', desc: 'Bens declarados no inventário' },
  { chave: 'arvore', titulo: 'Árvore Genealógica', href: '/arvore-genealogica', desc: 'Relações familiares identificadas' },
  { chave: 'analise', titulo: 'Análise IA', href: '/analise-ia', desc: 'Validações e inconsistências' },
]

const SELO_PROCESSO = {
  bloqueado: { status: 'rejeitado', texto: 'Protocolo bloqueado' },
  aberto: { status: 'em_analise', texto: 'Aguardando homologação' },
  concluido: { status: 'concluido', texto: 'Pronto para partilha' },
}

export default function Central() {
  const { processoId, lista, escolherProcesso, carregando: carregandoSessao } = useSessao()
  const { dados: resumo, erro, carregando } = useDados(
    () => (processoId ? apiProcessos.resumo(processoId) : Promise.resolve(null)),
    [processoId]
  )

  const processo = resumo ? resumo.processo : null

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">
              Central do Inventário
            </p>
            <h1 className="mt-1 font-display text-3xl font-semibold text-ink">
              {processo ? `Espólio de ${processo.nome_de_cujus}` : 'Inventário'}
            </h1>
            {lista.length > 1 && (
              <select
                value={processoId || ''}
                onChange={(e) => escolherProcesso(e.target.value)}
                className="mt-3 rounded-sm border border-ink/15 bg-white px-3 py-1.5 text-sm text-ink"
              >
                {lista.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.nome_de_cujus} {p.numero_processo ? `· ${p.numero_processo}` : ''}
                  </option>
                ))}
              </select>
            )}
          </div>
          <Link
            href="/inventario/novo"
            className="rounded-sm bg-ink px-4 py-2.5 text-sm font-medium text-parchment hover:bg-ink-soft"
          >
            + Novo inventário
          </Link>
        </div>

        <Alerta mensagem={erro} />

        {!carregandoSessao && !processoId && <SemProcesso />}

        {resumo && (
          <>
            <div className="grid gap-6 lg:grid-cols-3">
              <Card eyebrow="Progresso geral" title="Conclusão documental" className="lg:col-span-2">
                <ProgressoDocumental percentual={resumo.progresso_documental} />
                <div className="mt-6 grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="font-display text-2xl font-semibold text-ink">{resumo.documentos_enviados}</p>
                    <p className="text-xs text-slate">Documentos enviados</p>
                  </div>
                  <div>
                    <p className="font-display text-2xl font-semibold text-selo-warning">{resumo.pendencias_ativas}</p>
                    <p className="text-xs text-slate">Pendências ativas</p>
                  </div>
                  <div>
                    <p className="font-display text-2xl font-semibold text-ink">{resumo.herdeiros_cadastrados}</p>
                    <p className="text-xs text-slate">Herdeiros cadastrados</p>
                  </div>
                </div>
              </Card>

              <Card eyebrow="Andamento" title="Situação processual">
                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-slate">Fase atual</span>
                    <span className="font-medium text-ink">{resumo.fase}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate">Processo</span>
                    <span className="font-mono text-xs text-ink">{processo.numero_processo || 'não distribuído'}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate">Última movimentação</span>
                    <span className="text-ink">{formatarData(resumo.ultima_movimentacao)}</span>
                  </div>
                  <Selo {...SELO_PROCESSO[processo.status]} />
                </div>
              </Card>
            </div>

            <h2 className="mb-4 mt-10 font-display text-xl font-semibold text-ink">Módulos</h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {MODULOS.map((m) => {
                const pendencias = resumo.modulos[m.chave] || 0
                return (
                  <Link key={m.href} href={m.href}>
                    <Card className="h-full transition-shadow hover:shadow-md">
                      <div className="flex items-start justify-between">
                        <h3 className="font-display text-base font-semibold text-ink">{m.titulo}</h3>
                        {pendencias > 0 && (
                          <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-selo-warning/15 px-1 font-mono text-[11px] text-selo-warning">
                            {pendencias}
                          </span>
                        )}
                      </div>
                      <p className="mt-1.5 text-sm text-slate">{m.desc}</p>
                    </Card>
                  </Link>
                )
              })}
            </div>

            <h2 className="mb-4 mt-10 font-display text-xl font-semibold text-ink">Atividade recente</h2>
            <Card>
              {resumo.atividades.length === 0 ? (
                <p className="text-sm text-slate">Nenhuma atividade registrada.</p>
              ) : (
                <ul className="divide-y divide-ink/10">
                  {resumo.atividades.map((a) => (
                    <li key={a.id} className="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0">
                      <div className="flex items-center gap-3">
                        <Selo status={a.status} texto="" />
                        <span className="text-sm text-ink">{a.descricao}</span>
                      </div>
                      <span className="shrink-0 text-xs text-slate">{tempoRelativo(a.criado_em)}</span>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </>
        )}

        {carregando && processoId && <p className="mt-8 text-sm text-slate">Carregando…</p>}
      </main>
    </div>
  )
}
