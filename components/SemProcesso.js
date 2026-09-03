import Link from 'next/link'
import Card from '@/components/Card'

export default function SemProcesso() {
  return (
    <Card className="mt-8 text-center">
      <p className="font-display text-lg font-semibold text-ink">Nenhum inventário selecionado</p>
      <p className="mt-2 text-sm text-slate">
        Cadastre um novo inventário para começar a organizar os documentos, herdeiros e bens.
      </p>
      <Link
        href="/inventario/novo"
        className="mt-5 inline-block rounded-sm bg-ink px-4 py-2.5 text-sm font-medium text-parchment hover:bg-ink-soft"
      >
        + Novo inventário
      </Link>
    </Card>
  )
}
