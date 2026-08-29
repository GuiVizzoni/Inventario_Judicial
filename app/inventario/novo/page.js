'use client'

import { useState } from 'react'
import Navbar from '@/components/Navbar'
import Card from '@/components/Card'

const ETAPAS = ['Falecido (de cujus)', 'Herdeiros conhecidos', 'Bens conhecidos']

export default function NovoInventario() {
  const [etapa, setEtapa] = useState(0)

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-3xl px-6 py-10">
        <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">
          Novo processo
        </p>
        <h1 className="mt-1 font-display text-3xl font-semibold text-ink">
          Cadastro Inicial do Inventário
        </h1>
        <p className="mt-2 text-sm text-slate">
          Registre os dados básicos do de cujus, dos herdeiros e dos bens conhecidos
          para abrir o procedimento sucessório.
        </p>

        {/* Indicador de etapas — aqui a numeração é legítima: é um fluxo sequencial real */}
        <ol className="mt-8 flex items-center gap-2">
          {ETAPAS.map((nome, i) => (
            <li key={nome} className="flex flex-1 items-center gap-2">
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full font-mono text-xs ${
                  i <= etapa ? 'bg-ink text-parchment' : 'bg-ink/10 text-slate'
                }`}
              >
                {i + 1}
              </div>
              <span className={`hidden text-sm sm:block ${i === etapa ? 'text-ink' : 'text-slate'}`}>
                {nome}
              </span>
              {i < ETAPAS.length - 1 && <div className="h-px flex-1 bg-ink/10" />}
            </li>
          ))}
        </ol>

        <Card className="mt-8">
          {etapa === 0 && (
            <div className="space-y-5">
              <h3 className="font-display text-lg font-semibold text-ink">Dados do de cujus</h3>
              <Campo label="Nome completo" placeholder="Roberto Mendes da Silva" />
              <div className="grid gap-5 sm:grid-cols-2">
                <Campo label="CPF" placeholder="000.000.000-00" />
                <Campo label="Data do falecimento" tipo="date" />
              </div>
              <Campo label="Último domicílio" placeholder="Cidade / Estado" />
              <div>
                <label className="mb-1.5 block text-sm font-medium text-ink">
                  Certidão de óbito
                </label>
                <div className="rounded-sm border-2 border-dashed border-ink/15 px-4 py-6 text-center text-sm text-slate">
                  Arraste o arquivo ou <span className="text-bronze-dark">selecione no computador</span>
                </div>
              </div>
            </div>
          )}

          {etapa === 1 && (
            <div className="space-y-5">
              <h3 className="font-display text-lg font-semibold text-ink">Herdeiros conhecidos</h3>
              {[1, 2].map((n) => (
                <div key={n} className="grid gap-5 rounded-sm border border-ink/10 p-4 sm:grid-cols-2">
                  <Campo label="Nome completo" placeholder="Nome do herdeiro" />
                  <Campo label="Grau de parentesco" placeholder="Filho(a), cônjuge…" />
                </div>
              ))}
              <button className="text-sm font-medium text-bronze-dark hover:underline">
                + Adicionar outro herdeiro
              </button>
            </div>
          )}

          {etapa === 2 && (
            <div className="space-y-5">
              <h3 className="font-display text-lg font-semibold text-ink">Bens conhecidos</h3>
              <div className="grid gap-5 rounded-sm border border-ink/10 p-4 sm:grid-cols-2">
                <Campo label="Descrição do bem" placeholder="Imóvel, veículo, conta…" />
                <Campo label="Valor estimado" placeholder="R$ 0,00" />
              </div>
              <button className="text-sm font-medium text-bronze-dark hover:underline">
                + Adicionar outro bem
              </button>
            </div>
          )}

          <div className="mt-8 flex justify-between border-t border-ink/10 pt-6">
            <button
              onClick={() => setEtapa((e) => Math.max(0, e - 1))}
              disabled={etapa === 0}
              className="rounded-sm px-4 py-2 text-sm font-medium text-slate hover:text-ink disabled:opacity-40"
            >
              Voltar
            </button>
            <button
              onClick={() => setEtapa((e) => Math.min(ETAPAS.length - 1, e + 1))}
              className="rounded-sm bg-ink px-5 py-2.5 text-sm font-medium text-parchment hover:bg-ink-soft"
            >
              {etapa === ETAPAS.length - 1 ? 'Concluir cadastro' : 'Próxima etapa'}
            </button>
          </div>
        </Card>
      </main>
    </div>
  )
}

function Campo({ label, placeholder, tipo = 'text' }) {
  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium text-ink">{label}</label>
      <input
        type={tipo}
        placeholder={placeholder}
        className="w-full rounded-sm border border-ink/15 bg-white px-3 py-2.5 text-sm text-ink placeholder:text-slate/50 focus:border-bronze"
      />
    </div>
  )
}
