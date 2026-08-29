import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import Selo from '@/components/Selo'

const BENS = [
  { descricao: 'Apartamento — Jardins, São Paulo/SP', categoria: 'Imóvel', valor: 'R$ 1.250.000,00', status: 'em_analise' },
  { descricao: 'Veículo Honda Civic 2022', categoria: 'Móvel', valor: 'R$ 118.000,00', status: 'concluido' },
  { descricao: 'Conta corrente — Banco Ita', categoria: 'Financeiro', valor: 'R$ 87.400,00', status: 'concluido' },
  { descricao: 'Carteira de investimentos', categoria: 'Financeiro', valor: 'R$ 340.200,00', status: 'pendente' },
  { descricao: 'Sítio — Atibaia/SP', categoria: 'Imóvel rural', valor: 'R$ 620.000,00', status: 'pendente' },
]

const TOTAL = BENS.reduce((soma, b) => soma + Number(b.valor.replace(/[^\d,]/g, '').replace(',', '.')), 0)

export default function Patrimonio() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">Bens</p>
            <h1 className="mt-1 font-display text-3xl font-semibold text-ink">Gestão Patrimonial</h1>
            <p className="mt-2 text-sm text-slate">
              Organização e acompanhamento dos bens declarados no inventário.
            </p>
          </div>
          <button className="rounded-sm bg-ink px-4 py-2.5 text-sm font-medium text-parchment hover:bg-ink-soft">
            + Declarar bem
          </button>
        </div>

        <Card className="mt-8" eyebrow="Patrimônio total declarado" title={`R$ ${TOTAL.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`}>
          <p className="text-sm text-slate">Soma bruta dos bens registrados, antes de partilha e deduções legais.</p>
        </Card>

        <Card className="mt-6" title="Bens declarados">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-ink/10 text-xs uppercase tracking-wide text-slate">
                  <th className="py-2 pr-4 font-medium">Descrição</th>
                  <th className="py-2 pr-4 font-medium">Categoria</th>
                  <th className="py-2 pr-4 font-medium">Valor estimado</th>
                  <th className="py-2 pr-4 font-medium">Situação</th>
                </tr>
              </thead>
              <tbody>
                {BENS.map((b) => (
                  <tr key={b.descricao} className="border-b border-ink/5 last:border-0">
                    <td className="py-3 pr-4 text-ink">{b.descricao}</td>
                    <td className="py-3 pr-4 text-slate">{b.categoria}</td>
                    <td className="py-3 pr-4 font-mono text-xs text-ink">{b.valor}</td>
                    <td className="py-3 pr-4">
                      <Selo status={b.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </main>
    </div>
  )
}
