'use client'

import { useState } from 'react'
import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import Selo from '@/components/Selo'
import SemProcesso from '@/components/SemProcesso'
import { Alerta, BotaoSecundario } from '@/components/Campo'
import { useSessao } from '@/components/SessaoProvider'
import { useDados } from '@/lib/useDados'
import { analise as apiAnalise } from '@/lib/api'

export default function AnaliseIA() {
  const { processoId, carregando: carregandoSessao } = useSessao()
  const { dados, erro, setDados } = useDados(
    () => (processoId ? apiAnalise.obter(processoId) : Promise.resolve(null)),
    [processoId]
  )
  const [ocupado, setOcupado] = useState(false)
  const [erroAcao, setErroAcao] = useState(null)

  async function executar() {
    setOcupado(true)
    setErroAcao(null)
    try {
      setDados(await apiAnalise.executar(processoId))
    } catch (e) {
      setErroAcao(e.message)
    } finally {
      setOcupado(false)
    }
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">Inteligência Artificial</p>
            <h1 className="mt-1 font-display text-3xl font-semibold text-ink">Análise Inteligente do Inventário</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate">
              Validações documentais, inconsistências identificadas e recomendações
              geradas automaticamente pelos módulos de IA, preservando a decisão
              final ao profissional responsável.
            </p>
          </div>
          {processoId && (
            <BotaoSecundario onClick={executar} disabled={ocupado}>
              {ocupado ? 'Analisando…' : 'Executar nova análise'}
            </BotaoSecundario>
          )}
        </div>

        <div className="mt-6">
          <Alerta mensagem={erro || erroAcao} />
        </div>

        {!carregandoSessao && !processoId && <SemProcesso />}

        {dados && (
          <>
            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              <Card>
                <p className="font-display text-2xl font-semibold text-ink">{dados.itens_analisados}</p>
                <p className="text-xs text-slate">Itens analisados</p>
              </Card>
              <Card>
                <p className="font-display text-2xl font-semibold text-selo-success">{dados.validados}</p>
                <p className="text-xs text-slate">Validados sem ressalvas</p>
              </Card>
              <Card>
                <p className="font-display text-2xl font-semibold text-selo-warning">{dados.inconsistencias}</p>
                <p className="text-xs text-slate">Inconsistências encontradas</p>
              </Card>
            </div>

            <Card className="mt-6" title="Resultados da análise">
              {dados.resultados.length === 0 ? (
                <p className="text-sm text-slate">Nenhum documento analisado ainda.</p>
              ) : (
                <ul className="divide-y divide-ink/10">
                  {dados.resultados.map((v, i) => (
                    <li key={i} className="flex items-start justify-between gap-4 py-4 first:pt-0 last:pb-0">
                      <div>
                        <p className="text-sm font-medium text-ink">{v.titulo}</p>
                        <p className="mt-0.5 text-sm text-slate">{v.resultado}</p>
                      </div>
                      <Selo status={v.status} />
                    </li>
                  ))}
                </ul>
              )}
            </Card>

            <Card className="mt-6" eyebrow="Recomendação" title="Próxima providência sugerida">
              <p className="text-sm text-slate">{dados.recomendacao}</p>
            </Card>
          </>
        )}
      </main>
    </div>
  )
}
