'use client'

import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import SemProcesso from '@/components/SemProcesso'
import { Alerta } from '@/components/Campo'
import { useSessao } from '@/components/SessaoProvider'
import { useDados } from '@/lib/useDados'
import { analise as apiAnalise } from '@/lib/api'

function No({ nome, papel, raiz = false, preMorto = false, status }) {
  const borda = raiz ? 'border-bronze bg-bronze/10' : preMorto ? 'border-ink/20 border-dashed bg-white/60' : 'border-ink/15 bg-white'
  return (
    <div className={`flex w-40 flex-col items-center rounded-sm border px-3 py-2.5 text-center ${borda}`}>
      <p className={`text-xs font-medium leading-tight ${preMorto ? 'text-slate line-through' : 'text-ink'}`}>{nome}</p>
      <p className="mt-0.5 text-[10px] uppercase tracking-wide text-slate">{papel}</p>
      {status === 'concluido' && !raiz && <p className="mt-0.5 text-[9px] uppercase tracking-wide text-selo-success">confirmado</p>}
    </div>
  )
}

function Ramo({ herdeiro }) {
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="h-6 w-px bg-ink/20" />
      <No nome={herdeiro.nome} papel={herdeiro.parentesco} preMorto={herdeiro.pre_morto} status={herdeiro.status} />
      {herdeiro.representantes.length > 0 && (
        <div className="flex gap-6">
          {herdeiro.representantes.map((r) => (
            <Ramo key={r.id} herdeiro={r} />
          ))}
        </div>
      )}
    </div>
  )
}

export default function ArvoreGenealogica() {
  const { processoId, carregando: carregandoSessao } = useSessao()
  const { dados: arvore, erro } = useDados(
    () => (processoId ? apiAnalise.arvore(processoId) : Promise.resolve(null)),
    [processoId]
  )

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">Relações familiares</p>
        <h1 className="mt-1 font-display text-3xl font-semibold text-ink">Árvore Genealógica Automatizada</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate">
          Representação gerada a partir das certidões e informações cadastradas,
          evidenciando as relações relevantes para a sucessão patrimonial.
        </p>

        <div className="mt-6">
          <Alerta mensagem={erro} />
        </div>

        {!carregandoSessao && !processoId && <SemProcesso />}

        {arvore && (
          <>
            <Card className="mt-8 overflow-x-auto">
              <div className="flex min-w-[640px] flex-col items-center gap-8 py-6">
                <div className="flex items-center gap-6">
                  <No nome={arvore.de_cujus.nome} papel="De cujus" raiz />
                  {arvore.conjuges.map((c) => (
                    <div key={c.id} className="flex items-center gap-6">
                      <span className="text-slate">+</span>
                      <No nome={c.nome} papel={c.parentesco} status={c.status} />
                    </div>
                  ))}
                </div>

                {arvore.herdeiros.length > 0 && (
                  <>
                    <div className="h-8 w-px bg-ink/20" />
                    <div className="h-px w-[520px] bg-ink/20" />
                    <div className="flex flex-wrap justify-center gap-10">
                      {arvore.herdeiros.map((h) => (
                        <Ramo key={h.id} herdeiro={h} />
                      ))}
                    </div>
                  </>
                )}
                {arvore.herdeiros.length === 0 && <p className="text-sm text-slate">Nenhum herdeiro direto cadastrado.</p>}
              </div>
            </Card>

            <Card className="mt-6" title="Observações da análise automatizada">
              <ul className="space-y-2 text-sm text-slate">
                {arvore.observacoes.map((o, i) => (
                  <li key={i}>• {o}</li>
                ))}
              </ul>
            </Card>
          </>
        )}
      </main>
    </div>
  )
}
