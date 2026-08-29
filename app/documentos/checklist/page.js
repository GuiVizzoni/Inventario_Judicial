import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import Selo from '@/components/Selo'
import ProgressoDocumental from '@/components/ProgressoDocumental'

const CHECKLIST = [
  { nome: 'Certidão de óbito', status: 'concluido' },
  { nome: 'Certidão de casamento do de cujus', status: 'concluido' },
  { nome: 'RG e CPF de todos os herdeiros', status: 'em_analise' },
  { nome: 'Certidão de nascimento dos herdeiros', status: 'concluido' },
  { nome: 'Escritura ou matrícula dos imóveis', status: 'pendente' },
  { nome: 'Extratos bancários e de investimentos', status: 'pendente' },
  { nome: 'Certidão negativa de débitos (CND)', status: 'nao_iniciado' },
  { nome: 'Documento de veículos (CRLV/ATPV-e)', status: 'nao_iniciado' },
]

const TOTAL = CHECKLIST.length
const CONCLUIDOS = CHECKLIST.filter((d) => d.status === 'concluido').length

export default function Checklist() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-4xl px-6 py-10">
        <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">Documentação</p>
        <h1 className="mt-1 font-display text-3xl font-semibold text-ink">Checklist Documental</h1>
        <p className="mt-2 text-sm text-slate">
          Acompanhe os documentos exigidos, os arquivos já enviados e as pendências existentes.
        </p>

        <Card className="mt-8">
          <ProgressoDocumental
            percentual={Math.round((CONCLUIDOS / TOTAL) * 100)}
            rotulo={`${CONCLUIDOS} de ${TOTAL} itens concluídos`}
          />
        </Card>

        <Card className="mt-6" title="Itens exigidos">
          <ul className="divide-y divide-ink/10">
            {CHECKLIST.map((item) => (
              <li key={item.nome} className="flex items-center justify-between gap-4 py-3.5 first:pt-0 last:pb-0">
                <span className="text-sm text-ink">{item.nome}</span>
                <Selo status={item.status} />
              </li>
            ))}
          </ul>
        </Card>
      </main>
    </div>
  )
}
