'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const ITENS = [
  { rotulo: 'Central', href: '/central' },
  { rotulo: 'Documentação', href: '/documentos' },
  { rotulo: 'Herdeiros', href: '/herdeiros' },
  { rotulo: 'Patrimônio', href: '/patrimonio' },
  { rotulo: 'Árvore Genealógica', href: '/arvore-genealogica' },
  { rotulo: 'Análise IA', href: '/analise-ia' },
]

export default function Navbar({ processo = '0004521-89.2026.8.26.0100' }) {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-20 border-b border-ink/10 bg-parchment/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-6 py-4">
        <Link href="/central" className="shrink-0">
          <p className="font-display text-lg font-semibold leading-none text-ink">Inventário</p>
          <p className="font-mono text-[10px] tracking-wide text-slate">{processo}</p>
        </Link>

        <nav className="hidden flex-1 items-center gap-1 md:flex">
          {ITENS.map((item) => {
            const ativo = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-sm px-3 py-2 text-sm transition-colors ${
                  ativo
                    ? 'bg-ink text-parchment'
                    : 'text-ink/70 hover:bg-ink/5 hover:text-ink'
                }`}
              >
                {item.rotulo}
              </Link>
            )
          })}
        </nav>

        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <p className="text-sm font-medium text-ink">Ana Beatriz Ramos</p>
            <p className="text-xs text-slate">Advogada responsável</p>
          </div>
          <div className="flex h-9 w-9 items-center justify-center rounded-full border border-bronze/50 bg-bronze/10 font-display text-sm text-bronze-dark">
            AR
          </div>
        </div>
      </div>
    </header>
  )
}
