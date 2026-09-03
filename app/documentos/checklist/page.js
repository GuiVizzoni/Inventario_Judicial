'use client'

import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import Selo from '@/components/Selo'
import ProgressoDocumental from '@/components/ProgressoDocumental'
import SemProcesso from '@/components/SemProcesso'
import { Alerta } from '@/components/Campo'
import { useSessao } from '@/components/SessaoProvider'
import { useDados } from '@/lib/useDados'
import { processos as apiProcessos } from '@/lib/api'

export default function Checklist() {
  const { processoId, carregando: carregandoSessao } = useSessao()
  const { dados: checklist, erro } = useDados(
    () => (processoId ? apiProcessos.checklist(processoId) : Promise.resolve(null)),
    [processoId]
  )

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-4xl px-6 py-10">
        <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">Documentação</p>
        <h1 className="mt-1 font-display text-3xl font-semibold text-ink">Checklist Documental</h1>
        <p className="mt-2 text-sm text-slate">
          Acompanhe os documentos exigidos, os arquivos já enviados e as pendências existentes.
          Para documentos de acesso restrito, o sistema indica o portal competente.
        </p>

        <div className="mt-6">
          <Alerta mensagem={erro} />
        </div>

        {!carregandoSessao && !processoId && <SemProcesso />}

        {checklist && (
          <>
            <Card className="mt-8">
              <ProgressoDocumental
                percentual={checklist.percentual}
                rotulo={`${checklist.concluidos} de ${checklist.total} itens concluídos`}
              />
            </Card>

            <Card className="mt-6" title="Itens exigidos">
              <ul className="divide-y divide-ink/10">
                {checklist.itens.map((item) => (
                  <li key={item.tipo} className="py-3.5 first:pt-0 last:pb-0">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <span className="text-sm text-ink">{item.nome}</span>
                        <span className="ml-2 font-mono text-[10px] uppercase tracking-wide text-slate">
                          {item.bloqueante ? 'bloqueante' : item.obrigatorio ? 'obrigatório' : 'complementar'}
                          {item.origem === 'busca_automatica' ? ' · busca automática' : ''}
                        </span>
                      </div>
                      <Selo status={item.status} />
                    </div>
                    {item.status !== 'concluido' && (
                      <div className="mt-2 text-xs text-slate">
                        <p>{item.tutorial}</p>
                        {item.link_portal && (
                          <a href={item.link_portal} target="_blank" rel="noreferrer" className="mt-1 inline-block text-bronze-dark hover:underline">
                            Acessar portal competente ↗
                          </a>
                        )}
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </Card>
          </>
        )}
      </main>
    </div>
  )
}
