'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function Login() {
  const router = useRouter()
  const [carregando, setCarregando] = useState(false)

  function entrar(e) {
    e.preventDefault()
    setCarregando(true)
    setTimeout(() => router.push('/central'), 500)
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="grid w-full max-w-4xl overflow-hidden rounded-md border border-ink/10 bg-white/70 shadow-[0_1px_2px_rgba(16,24,39,0.04)] md:grid-cols-2">
        {/* Coluna institucional */}
        <div className="hidden flex-col justify-between bg-ink p-10 text-parchment md:flex">
          <div>
            <p className="font-mono text-xs uppercase tracking-widest text-bronze-soft">
              Procedimento sucessório
            </p>
            <h1 className="mt-3 font-display text-3xl font-semibold leading-tight">
              Plataforma de<br />Inventário Judicial
            </h1>
          </div>
          <div className="space-y-4 border-t border-parchment/15 pt-6 text-sm text-parchment/70">
            <p>
              Organização documental, gestão de herdeiros e análise assistida
              por Inteligência Artificial em um único ambiente.
            </p>
            <p className="font-mono text-[11px] text-parchment/50">
              Acesso restrito a usuários autorizados
            </p>
          </div>
        </div>

        {/* Formulário */}
        <div className="p-10">
          <h2 className="font-display text-2xl font-semibold text-ink">Entrar</h2>
          <p className="mt-1 text-sm text-slate">
            Informe suas credenciais para acessar a Central do Inventário.
          </p>

          <form className="mt-8 space-y-5" onSubmit={entrar}>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-ink" htmlFor="email">
                E-mail
              </label>
              <input
                id="email"
                type="email"
                required
                placeholder="nome@escritorio.com.br"
                className="w-full rounded-sm border border-ink/15 bg-white px-3 py-2.5 text-sm text-ink placeholder:text-slate/50 focus:border-bronze"
              />
            </div>

            <div>
              <div className="mb-1.5 flex items-center justify-between">
                <label className="block text-sm font-medium text-ink" htmlFor="senha">
                  Senha
                </label>
                <a href="#" className="text-xs text-bronze-dark hover:underline">
                  Esqueci minha senha
                </a>
              </div>
              <input
                id="senha"
                type="password"
                required
                placeholder="••••••••"
                className="w-full rounded-sm border border-ink/15 bg-white px-3 py-2.5 text-sm text-ink focus:border-bronze"
              />
            </div>

            <label className="flex items-center gap-2 text-sm text-slate">
              <input type="checkbox" className="h-4 w-4 rounded-sm border-ink/30" />
              Manter conectado neste dispositivo
            </label>

            <button
              type="submit"
              disabled={carregando}
              className="w-full rounded-sm bg-ink py-2.5 text-sm font-medium text-parchment transition-colors hover:bg-ink-soft disabled:opacity-60"
            >
              {carregando ? 'Autenticando…' : 'Acessar plataforma'}
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-slate">
            Ainda não possui acesso?{' '}
            <a href="#" className="text-bronze-dark hover:underline">
              Solicite ao administrador do escritório
            </a>
          </p>
        </div>
      </div>
    </main>
  )
}
