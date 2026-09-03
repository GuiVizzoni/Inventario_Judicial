'use client'

import { useState } from 'react'
import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Card from '@/components/Card'
import Selo from '@/components/Selo'
import SemProcesso from '@/components/SemProcesso'
import { Alerta, BotaoPrimario, BotaoSecundario, Selecao } from '@/components/Campo'
import { useSessao } from '@/components/SessaoProvider'
import { useDados } from '@/lib/useDados'
import { catalogo as apiCatalogo, documentos as apiDocumentos } from '@/lib/api'
import { formatarDataHora, formatarTamanho } from '@/lib/formatadores'

export default function Documentos() {
  const { processoId, processo, carregando: carregandoSessao } = useSessao()
  const { dados: lista, erro, recarregar } = useDados(
    () => (processoId ? apiDocumentos.listar(processoId) : Promise.resolve([])),
    [processoId]
  )
  const { dados: tipos } = useDados(() => apiCatalogo.documentos(), [])

  const [mostrarEnvio, setMostrarEnvio] = useState(false)
  const [tipo, setTipo] = useState('certidao_obito')
  const [arquivo, setArquivo] = useState(null)
  const [mensagem, setMensagem] = useState(null)
  const [erroAcao, setErroAcao] = useState(null)
  const [ocupado, setOcupado] = useState(false)
  const [selecionado, setSelecionado] = useState(null)

  async function executar(acao, sucesso) {
    setOcupado(true)
    setErroAcao(null)
    setMensagem(null)
    try {
      await acao()
      if (sucesso) setMensagem(sucesso)
      await recarregar()
      setTimeout(recarregar, 2000)
    } catch (e) {
      setErroAcao(e.message)
    } finally {
      setOcupado(false)
    }
  }

  async function enviar(e) {
    e.preventDefault()
    if (!arquivo) {
      setErroAcao('Selecione um arquivo PDF.')
      return
    }
    await executar(async () => {
      await apiDocumentos.enviar(processoId, tipo, arquivo)
      setArquivo(null)
      setMostrarEnvio(false)
    }, 'Documento recebido. O processamento roda em segundo plano e a tabela é atualizada em instantes.')
  }

  async function verDetalhe(doc) {
    try {
      const detalhe = await apiDocumentos.obter(processoId, doc.id)
      setSelecionado(detalhe)
    } catch (e) {
      setErroAcao(e.message)
    }
  }

  const opcoesTipo = (tipos || []).map((t) => ({ valor: t.tipo, rotulo: t.nome }))

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">Documentação</p>
            <h1 className="mt-1 font-display text-3xl font-semibold text-ink">Gerenciamento de Documentos</h1>
          </div>
          {processoId && (
            <div className="flex flex-wrap gap-3">
              <Link href="/documentos/checklist" className="rounded-sm border border-ink/15 px-4 py-2.5 text-sm font-medium text-ink hover:bg-ink/5">
                Ver checklist
              </Link>
              <BotaoSecundario
                disabled={ocupado || !processo || processo.status === 'bloqueado'}
                title={processo && processo.status === 'bloqueado' ? 'Disponível após a validação da certidão de óbito' : ''}
                onClick={() => executar(() => apiDocumentos.buscaAutomatica(processoId), 'Busca automática de certidões negativas executada.')}
              >
                Buscar certidões negativas
              </BotaoSecundario>
              <button
                type="button"
                onClick={() => setMostrarEnvio((v) => !v)}
                className="rounded-sm bg-ink px-4 py-2.5 text-sm font-medium text-parchment hover:bg-ink-soft"
              >
                + Enviar documento
              </button>
            </div>
          )}
        </div>

        {!carregandoSessao && !processoId && <SemProcesso />}

        <div className="mt-6 space-y-3">
          <Alerta mensagem={erro || erroAcao} />
          <Alerta mensagem={mensagem} tipo="sucesso" />
        </div>

        {mostrarEnvio && processoId && (
          <Card className="mt-6" eyebrow="Upload assistido" title="Enviar documento">
            <form onSubmit={enviar} className="grid gap-5 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
              <Selecao label="Tipo documental" valor={tipo} aoMudar={setTipo} opcoes={opcoesTipo} />
              <div>
                <label className="mb-1.5 block text-sm font-medium text-ink">Arquivo PDF</label>
                <input
                  type="file"
                  accept="application/pdf"
                  onChange={(e) => setArquivo(e.target.files[0] || null)}
                  className="block w-full text-sm text-slate file:mr-3 file:rounded-sm file:border file:border-ink/15 file:bg-white file:px-3 file:py-2 file:text-sm file:text-ink"
                />
              </div>
              <BotaoPrimario carregando={ocupado}>{ocupado ? 'Enviando…' : 'Enviar'}</BotaoPrimario>
            </form>
            {tipos && (
              <p className="mt-4 text-xs text-slate">{(tipos.find((t) => t.tipo === tipo) || {}).tutorial}</p>
            )}
          </Card>
        )}

        {processoId && (
          <Card className="mt-8" title="Arquivos enviados" action={<button type="button" onClick={recarregar} className="text-xs text-bronze-dark hover:underline">Atualizar</button>}>
            {!lista || lista.length === 0 ? (
              <p className="text-sm text-slate">Nenhum documento enviado até o momento.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-ink/10 text-xs uppercase tracking-wide text-slate">
                      <th className="py-2 pr-4 font-medium">Arquivo</th>
                      <th className="py-2 pr-4 font-medium">Categoria</th>
                      <th className="py-2 pr-4 font-medium">Tamanho</th>
                      <th className="py-2 pr-4 font-medium">Enviado em</th>
                      <th className="py-2 pr-4 font-medium">Situação</th>
                      <th className="py-2 pr-4 font-medium"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {lista.map((doc) => (
                      <tr key={doc.id} className="border-b border-ink/5 last:border-0">
                        <td className="py-3 pr-4">
                          <button type="button" onClick={() => verDetalhe(doc)} className="text-left text-ink hover:underline">
                            {doc.nome_arquivo}
                          </button>
                          <p className="text-xs text-slate">
                            {doc.tipo_nome}
                            {doc.origem === 'busca_automatica' ? ' · busca automática' : ''}
                          </p>
                        </td>
                        <td className="py-3 pr-4 text-slate">{doc.categoria}</td>
                        <td className="py-3 pr-4 font-mono text-xs text-slate">{formatarTamanho(doc.tamanho_bytes)}</td>
                        <td className="py-3 pr-4 text-slate">{formatarDataHora(doc.recebido_em)}</td>
                        <td className="py-3 pr-4">
                          <Selo status={doc.status_validacao} />
                        </td>
                        <td className="py-3 pr-4 text-right text-xs">
                          <button type="button" onClick={() => apiDocumentos.baixar(processoId, doc.id, doc.nome_arquivo).catch((e) => setErroAcao(e.message))} className="text-bronze-dark hover:underline">
                            abrir
                          </button>
                          <span className="text-slate"> · </span>
                          <button type="button" disabled={ocupado} onClick={() => executar(() => apiDocumentos.reprocessar(processoId, doc.id), 'Documento reprocessado.')} className="text-bronze-dark hover:underline">
                            reprocessar
                          </button>
                          <span className="text-slate"> · </span>
                          <button
                            type="button"
                            disabled={ocupado}
                            onClick={() => {
                              if (window.confirm(`Excluir ${doc.nome_arquivo}?`)) executar(() => apiDocumentos.remover(processoId, doc.id), 'Documento excluído.')
                            }}
                            className="text-selo-danger hover:underline"
                          >
                            excluir
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        )}

        {selecionado && (
          <Card
            className="mt-6"
            eyebrow={selecionado.tipo_nome}
            title={selecionado.nome_arquivo}
            action={
              <button type="button" onClick={() => setSelecionado(null)} className="text-xs text-slate hover:text-ink">
                fechar
              </button>
            }
          >
            <div className="grid gap-6 md:grid-cols-2">
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-3">
                  <Selo status={selecionado.status_validacao} />
                  {selecionado.metodo_extracao && <span className="font-mono text-xs text-slate">extração: {selecionado.metodo_extracao}</span>}
                </div>
                <p className="text-slate">{selecionado.motivo_status || selecionado.erro_processamento || 'Aguardando processamento.'}</p>
                {selecionado.tipo_detectado && selecionado.tipo_detectado !== selecionado.tipo && (
                  <p className="text-selo-danger">Tipo detectado pelo modelo: {selecionado.tipo_detectado}</p>
                )}
                <h4 className="pt-2 font-medium text-ink">Entidades extraídas</h4>
                {selecionado.entidades.length === 0 ? (
                  <p className="text-slate">Nenhuma entidade extraída.</p>
                ) : (
                  <ul className="divide-y divide-ink/10">
                    {selecionado.entidades.map((e) => (
                      <li key={e.id} className="flex items-start justify-between gap-4 py-2">
                        <span className="font-mono text-xs text-slate">{e.chave}</span>
                        <span className="text-right text-ink">{e.valor}</span>
                      </li>
                    ))}
                  </ul>
                )}
                {selecionado.entidades.length > 0 && (
                  <p className="pt-2 font-mono text-[11px] text-slate">
                    modelo {selecionado.entidades[0].modelo_llm} · versão {selecionado.entidades[0].versao_extracao} · confiança {Math.round(selecionado.entidades[0].confianca * 100)}%
                  </p>
                )}
              </div>
              <div>
                <h4 className="mb-2 text-sm font-medium text-ink">Texto extraído</h4>
                <pre className="max-h-80 overflow-auto whitespace-pre-wrap rounded-sm border border-ink/10 bg-white p-3 font-mono text-[11px] text-slate">
                  {selecionado.texto_extraido || 'Sem texto.'}
                </pre>
              </div>
            </div>
          </Card>
        )}
      </main>
    </div>
  )
}
