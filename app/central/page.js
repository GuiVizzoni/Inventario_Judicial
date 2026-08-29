import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import Selo from '@/components/Selo'
import ProgressoDocumental from '@/components/ProgressoDocumental'
import Link from 'next/link'

const MODULOS = [
  { titulo: 'Documentação', href: '/documentos', desc: 'Envio e checklist de documentos', pendencias: 3 },
  { titulo: 'Herdeiros', href: '/herdeiros', desc: 'Cadastro e dados sucessórios', pendencias: 0 },
  { titulo: 'Patrimônio', href: '/patrimonio', desc: 'Bens declarados no inventário', pendencias: 1 },
  { titulo: 'Árvore Genealógica', href: '/arvore-genealogica', desc: 'Relações familiares identificadas', pendencias: 0 },
  { titulo: 'Análise IA', href: '/analise-ia', desc: 'Validações e inconsistências', pendencias: 2 },
]

const ATIVIDADES = [
  { texto: 'Certidão de óbito validada automaticamente', tempo: 'há 2 horas', status: 'concluido' },
  { texto: 'Pendência identificada: RG do herdeiro Carlos Mendes', tempo: 'há 5 horas', status: 'pendente' },
  { texto: 'Escritura do imóvel em análise pela IA', tempo: 'ontem', status: 'em_analise' },
  { texto: 'Herdeira Juliana Mendes cadastrada', tempo: 'há 2 dias', status: 'concluido' },
]

export default function Central() {
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
              Espólio de Roberto Mendes da Silva
            </h1>
          </div>
          <Link
            href="/inventario/novo"
            className="rounded-sm bg-ink px-4 py-2.5 text-sm font-medium text-parchment hover:bg-ink-soft"
          >
            + Novo inventário
          </Link>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Progresso geral */}
          <Card
            eyebrow="Progresso geral"
            title="Conclusão documental"
            className="lg:col-span-2"
          >
            <ProgressoDocumental percentual={68} />
            <div className="mt-6 grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="font-display text-2xl font-semibold text-ink">12</p>
                <p className="text-xs text-slate">Documentos enviados</p>
              </div>
              <div>
                <p className="font-display text-2xl font-semibold text-selo-warning">6</p>
                <p className="text-xs text-slate">Pendências ativas</p>
              </div>
              <div>
                <p className="font-display text-2xl font-semibold text-ink">4</p>
                <p className="text-xs text-slate">Herdeiros cadastrados</p>
              </div>
            </div>
          </Card>

          {/* Andamento processual */}
          <Card eyebrow="Andamento" title="Situação processual">
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-slate">Fase atual</span>
                <span className="font-medium text-ink">Instrução documental</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate">Processo</span>
                <span className="font-mono text-xs text-ink">0004521-89.2026.8.26.0100</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate">Última movimentação</span>
                <span className="text-ink">28/08/2026</span>
              </div>
              <Selo status="em_analise" texto="Aguardando homologação" />
            </div>
          </Card>
        </div>

        {/* Módulos */}
        <h2 className="mb-4 mt-10 font-display text-xl font-semibold text-ink">Módulos</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {MODULOS.map((m) => (
            <Link key={m.href} href={m.href}>
              <Card className="h-full transition-shadow hover:shadow-md">
                <div className="flex items-start justify-between">
                  <h3 className="font-display text-base font-semibold text-ink">{m.titulo}</h3>
                  {m.pendencias > 0 && (
                    <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-selo-warning/15 px-1 font-mono text-[11px] text-selo-warning">
                      {m.pendencias}
                    </span>
                  )}
                </div>
                <p className="mt-1.5 text-sm text-slate">{m.desc}</p>
              </Card>
            </Link>
          ))}
        </div>

        {/* Atividades recentes */}
        <h2 className="mb-4 mt-10 font-display text-xl font-semibold text-ink">Atividade recente</h2>
        <Card>
          <ul className="divide-y divide-ink/10">
            {ATIVIDADES.map((a, i) => (
              <li key={i} className="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0">
                <div className="flex items-center gap-3">
                  <Selo status={a.status} texto="" />
                  <span className="text-sm text-ink">{a.texto}</span>
                </div>
                <span className="shrink-0 text-xs text-slate">{a.tempo}</span>
              </li>
            ))}
          </ul>
        </Card>
      </main>
    </div>
  )
}
