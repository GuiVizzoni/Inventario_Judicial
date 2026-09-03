export function formatarData(valor) {
  if (!valor) return '—'
  const data = valor.length <= 10 ? new Date(`${valor}T00:00:00`) : new Date(valor)
  if (Number.isNaN(data.getTime())) return valor
  return data.toLocaleDateString('pt-BR')
}

export function formatarDataHora(valor) {
  if (!valor) return '—'
  const data = new Date(valor)
  if (Number.isNaN(data.getTime())) return valor
  return data.toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

export function tempoRelativo(valor) {
  if (!valor) return ''
  const data = new Date(valor)
  const segundos = Math.max(0, Math.round((Date.now() - data.getTime()) / 1000))
  if (segundos < 60) return 'agora mesmo'
  const minutos = Math.round(segundos / 60)
  if (minutos < 60) return `há ${minutos} min`
  const horas = Math.round(minutos / 60)
  if (horas < 24) return `há ${horas} hora${horas > 1 ? 's' : ''}`
  const dias = Math.round(horas / 24)
  if (dias === 1) return 'ontem'
  if (dias < 30) return `há ${dias} dias`
  return data.toLocaleDateString('pt-BR')
}

export function formatarMoeda(valor) {
  const numero = Number(valor || 0)
  return numero.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export function formatarTamanho(bytes) {
  const n = Number(bytes || 0)
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`
  return `${(n / (1024 * 1024)).toFixed(1)} MB`
}

export function iniciais(nome) {
  return (nome || '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0])
    .join('')
    .toUpperCase()
}

export const CATEGORIAS_BEM = [
  { valor: 'imovel', rotulo: 'Imóvel' },
  { valor: 'imovel_rural', rotulo: 'Imóvel rural' },
  { valor: 'movel', rotulo: 'Móvel' },
  { valor: 'financeiro', rotulo: 'Financeiro' },
  { valor: 'outro', rotulo: 'Outro' },
]

export function rotuloCategoriaBem(valor) {
  const item = CATEGORIAS_BEM.find((c) => c.valor === valor)
  return item ? item.rotulo : valor
}

export const ROTULOS_STATUS_PROCESSO = {
  bloqueado: 'Protocolo bloqueado',
  aberto: 'Em instrução',
  concluido: 'Concluído',
}
