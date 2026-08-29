import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import Selo from '@/components/Selo'

const VALIDACOES = [
  {
    titulo: 'Certidão de óbito',
    resultado: 'Dados consistentes com o cadastro do de cujus',
    status: 'concluido',
  },
  {
    titulo: 'Escritura do apartamento — Jardins',
    resultado: 'Divergência entre metragem informada e registrada em matrícula',
    status: 'pendente',
  },
  {
    titulo: 'RG — Carlos Mendes da Silva',
    resultado: 'Documento ilegível em parte; reenvio recomendado',
    status: 'pendente',
  },
  {
    titulo: 'Certidão de casamento',
    resultado: 'Regime de bens extraído e associado corretamente',
    status: 'concluido',
  },
]

export default function AnaliseIA() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">
          Inteligência Artificial
        </p>
        <h1 className="mt-1 font-display text-3xl font-semibold text-ink">
          Análise Inteligente do Inventário
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-slate">
          Validações documentais, inconsistências identificadas e recomendações
          geradas automaticamente pelos módulos de IA, preservando a decisão
          final ao profissional responsável.
        </p>

        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          <Card>
            <p className="font-display text-2xl font-semibold text-ink">18</p>
            <p className="text-xs text-slate">Itens analisados</p>
          </Card>
          <Card>
            <p className="font-display text-2xl font-semibold text-selo-success">14</p>
            <p className="text-xs text-slate">Validados sem ressalvas</p>
          </Card>
          <Card>
            <p className="font-display text-2xl font-semibold text-selo-warning">4</p>
            <p className="text-xs text-slate">Inconsistências encontradas</p>
          </Card>
        </div>

        <Card className="mt-6" title="Resultados da análise">
          <ul className="divide-y divide-ink/10">
            {VALIDACOES.map((v) => (
              <li key={v.titulo} className="flex items-start justify-between gap-4 py-4 first:pt-0 last:pb-0">
                <div>
                  <p className="text-sm font-medium text-ink">{v.titulo}</p>
                  <p className="mt-0.5 text-sm text-slate">{v.resultado}</p>
                </div>
                <Selo status={v.status} />
              </li>
            ))}
          </ul>
        </Card>

        <Card className="mt-6" eyebrow="Recomendação" title="Próxima providência sugerida">
          <p className="text-sm text-slate">
            Solicitar reenvio do RG do herdeiro Carlos Mendes da Silva e confirmar
            a metragem do apartamento junto ao cartório de registro de imóveis
            antes de prosseguir para a fase de partilha.
          </p>
        </Card>
      </main>
    </div>
  )
}
