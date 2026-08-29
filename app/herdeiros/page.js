import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import Selo from '@/components/Selo'

const HERDEIROS = [
  { nome: 'Carlos Mendes da Silva', parentesco: 'Filho', cpf: '123.456.789-00', status: 'pendente' },
  { nome: 'Juliana Mendes Ribeiro', parentesco: 'Filha', cpf: '234.567.890-11', status: 'concluido' },
  { nome: 'Marta Aparecida Silva', parentesco: 'Cônjuge', cpf: '345.678.901-22', status: 'concluido' },
  { nome: 'Pedro Henrique Mendes', parentesco: 'Filho', cpf: '456.789.012-33', status: 'em_analise' },
]

export default function Herdeiros() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">
              Sucessão
            </p>
            <h1 className="mt-1 font-display text-3xl font-semibold text-ink">Gestão de Herdeiros</h1>
            <p className="mt-2 text-sm text-slate">
              Consulte e atualize os dados sucessórios cadastrados no processo.
            </p>
          </div>
          <button className="rounded-sm bg-ink px-4 py-2.5 text-sm font-medium text-parchment hover:bg-ink-soft">
            + Cadastrar herdeiro
          </button>
        </div>

        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          {HERDEIROS.map((h) => (
            <Card key={h.cpf}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 items-center justify-center rounded-full bg-ink/5 font-display text-sm text-ink">
                    {h.nome.split(' ').map((p) => p[0]).slice(0, 2).join('')}
                  </div>
                  <div>
                    <p className="font-medium text-ink">{h.nome}</p>
                    <p className="text-xs text-slate">{h.parentesco}</p>
                  </div>
                </div>
                <Selo status={h.status} />
              </div>
              <div className="mt-4 flex items-center justify-between border-t border-ink/10 pt-3 text-xs">
                <span className="font-mono text-slate">{h.cpf}</span>
                <button className="text-bronze-dark hover:underline">Ver detalhes</button>
              </div>
            </Card>
          ))}
        </div>
      </main>
    </div>
  )
}
