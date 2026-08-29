import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import Selo from '@/components/Selo'
import Link from 'next/link'

const DOCUMENTOS = [
  { nome: 'certidao_obito_roberto.pdf', categoria: 'Certidões', tamanho: '412 KB', data: '12/08/2026', status: 'concluido' },
  { nome: 'rg_carlos_mendes.pdf', categoria: 'Documentos pessoais', tamanho: '1.1 MB', data: '15/08/2026', status: 'pendente' },
  { nome: 'escritura_apartamento_jardins.pdf', categoria: 'Bens imóveis', tamanho: '3.4 MB', data: '20/08/2026', status: 'em_analise' },
  { nome: 'extrato_investimentos_2025.pdf', categoria: 'Bens financeiros', tamanho: '820 KB', data: '22/08/2026', status: 'em_analise' },
  { nome: 'certidao_casamento.pdf', categoria: 'Certidões', tamanho: '298 KB', data: '12/08/2026', status: 'concluido' },
]

export default function Documentos() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">
              Documentação
            </p>
            <h1 className="mt-1 font-display text-3xl font-semibold text-ink">
              Gerenciamento de Documentos
            </h1>
          </div>
          <div className="flex gap-3">
            <Link
              href="/documentos/checklist"
              className="rounded-sm border border-ink/15 px-4 py-2.5 text-sm font-medium text-ink hover:bg-ink/5"
            >
              Ver checklist
            </Link>
            <button className="rounded-sm bg-ink px-4 py-2.5 text-sm font-medium text-parchment hover:bg-ink-soft">
              + Enviar documento
            </button>
          </div>
        </div>

        <Card className="mt-8" title="Arquivos enviados">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-ink/10 text-xs uppercase tracking-wide text-slate">
                  <th className="py-2 pr-4 font-medium">Arquivo</th>
                  <th className="py-2 pr-4 font-medium">Categoria</th>
                  <th className="py-2 pr-4 font-medium">Tamanho</th>
                  <th className="py-2 pr-4 font-medium">Enviado em</th>
                  <th className="py-2 pr-4 font-medium">Situação</th>
                </tr>
              </thead>
              <tbody>
                {DOCUMENTOS.map((doc) => (
                  <tr key={doc.nome} className="border-b border-ink/5 last:border-0">
                    <td className="py-3 pr-4 text-ink">{doc.nome}</td>
                    <td className="py-3 pr-4 text-slate">{doc.categoria}</td>
                    <td className="py-3 pr-4 font-mono text-xs text-slate">{doc.tamanho}</td>
                    <td className="py-3 pr-4 text-slate">{doc.data}</td>
                    <td className="py-3 pr-4">
                      <Selo status={doc.status} />
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
