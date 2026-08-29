const ESTILOS = {
  concluido: {
    cor: 'text-selo-success border-selo-success',
    ponto: 'bg-selo-success',
    rotulo: 'Concluído',
  },
  em_analise: {
    cor: 'text-bronze-dark border-bronze',
    ponto: 'bg-bronze',
    rotulo: 'Em análise',
  },
  pendente: {
    cor: 'text-selo-warning border-selo-warning',
    ponto: 'bg-selo-warning',
    rotulo: 'Pendente',
  },
  rejeitado: {
    cor: 'text-selo-danger border-selo-danger',
    ponto: 'bg-selo-danger',
    rotulo: 'Rejeitado',
  },
  nao_iniciado: {
    cor: 'text-selo-neutral border-selo-neutral',
    ponto: 'bg-selo-neutral',
    rotulo: 'Não iniciado',
  },
}

/**
 * Selo: badge circular-angular que remete a um carimbo/selo cartorário.
 * Usado de forma consistente em todas as telas para status de
 * documentos, herdeiros e bens.
 */
export default function Selo({ status = 'pendente', texto }) {
  const estilo = ESTILOS[status] || ESTILOS.pendente
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-sm border px-2 py-0.5 text-[11px] font-mono uppercase tracking-wide ${estilo.cor} bg-white/60`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${estilo.ponto}`} />
      {texto || estilo.rotulo}
    </span>
  )
}
