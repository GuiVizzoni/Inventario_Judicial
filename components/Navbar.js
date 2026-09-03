'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useSessao } from '@/components/SessaoProvider'
import { iniciais } from '@/lib/formatadores'

const ITENS = [
  { rotulo: 'Central', href: '/central' },
  { rotulo: 'Documentação', href: '/documentos' },
  { rotulo: 'Herdeiros', href: '/herdeiros' },
  { rotulo: 'Patrimônio', href: '/patrimonio' },
  { rotulo: 'Árvore Genealógica', href: '/arvore-genealogica' },
  { rotulo: 'Análise IA', href: '/analise-ia' },
]

const PAPEIS = {
  advogado: 'Advogado(a) responsável',
  administrador: 'Administrador(a)',
}

export default function Navbar() {
  const pathname = usePathname()
  const { usuario, processo, sair } = useSessao()

  return (
    <header className="sticky top-0 z-20 border-b border-ink/10 bg-parchment/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-6 py-4">
        <Link href="/central" className="shrink-0">
          <p className="font-display text-lg font-semibold leading-none text-ink">Inventário</p>
          <p className="font-mono text-[10px] tracking-wide text-slate">
            {processo ? processo.numero_processo || `Espólio de ${processo.nome_de_cujus}` : 'nenhum processo selecionado'}
          </p>
        </Link>

        <nav className="hidden flex-1 items-center gap-1 md:flex">
          {ITENS.map((item) => {
            const ativo = pathname === item.href || pathname.startsWith(`${item.href}/`)
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`rounded-sm px-3 py-2 text-sm transition-colors ${
                  ativo ? 'bg-ink text-parchment' : 'text-ink/70 hover:bg-ink/5 hover:text-ink'
                }`}
              >
                {item.rotulo}
              </Link>
            )
          })}
        </nav>

        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <p className="text-sm font-medium text-ink">{usuario ? usuario.nome : '…'}</p>
            <p className="text-xs text-slate">{usuario ? PAPEIS[usuario.papel] || usuario.papel : ''}</p>
          </div>
          <button
            type="button"
            onClick={sair}
            title="Sair"
            className="flex h-9 w-9 items-center justify-center rounded-full border border-bronze/50 bg-bronze/10 font-display text-sm text-bronze-dark hover:bg-bronze/20"
          >
            {usuario ? iniciais(usuario.nome) : '?'}
          </button>
        </div>
      </div>
    </header>
  )
}
