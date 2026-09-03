const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function obterToken() {
  try {
    return localStorage.getItem('token')
  } catch {
    return null
  }
}

export function salvarSessao(token) {
  try {
    localStorage.setItem('token', token)
  } catch {}
}

export function limparSessao() {
  try {
    localStorage.removeItem('token')
    localStorage.removeItem('processoId')
  } catch {}
}

function mensagemDeErro(dados, status) {
  if (dados && dados.detail) {
    if (typeof dados.detail === 'string') return dados.detail
    if (Array.isArray(dados.detail)) {
      return dados.detail.map((d) => `${(d.loc || []).slice(1).join('.')}: ${d.msg}`).join('; ')
    }
  }
  return `Erro ${status}`
}

export async function api(caminho, { metodo = 'GET', corpo, formulario } = {}) {
  const headers = {}
  const token = obterToken()
  if (token) headers.Authorization = `Bearer ${token}`
  if (corpo !== undefined) headers['Content-Type'] = 'application/json'

  const resposta = await fetch(`${BASE}${caminho}`, {
    method: metodo,
    headers,
    body: formulario ? formulario : corpo !== undefined ? JSON.stringify(corpo) : undefined,
  })

  if (resposta.status === 401) {
    limparSessao()
    if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
    throw new Error('Sessão expirada')
  }
  if (resposta.status === 204) return null

  const dados = await resposta.json().catch(() => null)
  if (!resposta.ok) throw new Error(mensagemDeErro(dados, resposta.status))
  return dados
}

async function baixarComToken(caminho, nome) {
  const headers = {}
  const token = obterToken()
  if (token) headers.Authorization = `Bearer ${token}`
  const resposta = await fetch(`${BASE}${caminho}`, { headers })
  if (!resposta.ok) throw new Error(`Erro ${resposta.status} ao baixar arquivo`)
  const blob = await resposta.blob()
  const url = URL.createObjectURL(blob)
  window.open(url, '_blank')
  setTimeout(() => URL.revokeObjectURL(url), 60000)
}

export const auth = {
  login: (email, senha) => api('/auth/login', { metodo: 'POST', corpo: { email, senha } }),
  me: () => api('/auth/me'),
}

export const catalogo = {
  documentos: () => api('/catalogo/documentos'),
}

export const processos = {
  listar: () => api('/processos'),
  criar: (dados) => api('/processos', { metodo: 'POST', corpo: dados }),
  obter: (id) => api(`/processos/${id}`),
  atualizar: (id, dados) => api(`/processos/${id}`, { metodo: 'PATCH', corpo: dados }),
  remover: (id) => api(`/processos/${id}`, { metodo: 'DELETE' }),
  resumo: (id) => api(`/processos/${id}/resumo`),
  checklist: (id) => api(`/processos/${id}/checklist`),
  eventos: (id) => api(`/processos/${id}/eventos`),
}

export const documentos = {
  listar: (pid) => api(`/processos/${pid}/documentos`),
  obter: (pid, id) => api(`/processos/${pid}/documentos/${id}`),
  enviar: (pid, tipo, arquivo) => {
    const formulario = new FormData()
    formulario.append('tipo', tipo)
    formulario.append('arquivo', arquivo)
    return api(`/processos/${pid}/documentos`, { metodo: 'POST', formulario })
  },
  reprocessar: (pid, id) => api(`/processos/${pid}/documentos/${id}/reprocessar`, { metodo: 'POST' }),
  remover: (pid, id) => api(`/processos/${pid}/documentos/${id}`, { metodo: 'DELETE' }),
  buscaAutomatica: (pid) => api(`/processos/${pid}/documentos/busca-automatica`, { metodo: 'POST' }),
  baixar: (pid, id, nome) => baixarComToken(`/processos/${pid}/documentos/${id}/arquivo`, nome),
}

export const herdeiros = {
  listar: (pid) => api(`/processos/${pid}/herdeiros`),
  criar: (pid, dados) => api(`/processos/${pid}/herdeiros`, { metodo: 'POST', corpo: dados }),
  atualizar: (pid, id, dados) => api(`/processos/${pid}/herdeiros/${id}`, { metodo: 'PATCH', corpo: dados }),
  remover: (pid, id) => api(`/processos/${pid}/herdeiros/${id}`, { metodo: 'DELETE' }),
}

export const bens = {
  listar: (pid) => api(`/processos/${pid}/bens`),
  criar: (pid, dados) => api(`/processos/${pid}/bens`, { metodo: 'POST', corpo: dados }),
  atualizar: (pid, id, dados) => api(`/processos/${pid}/bens/${id}`, { metodo: 'PATCH', corpo: dados }),
  remover: (pid, id) => api(`/processos/${pid}/bens/${id}`, { metodo: 'DELETE' }),
}

export const pendencias = {
  listar: (pid, apenasAbertas = true) => api(`/processos/${pid}/pendencias?apenas_abertas=${apenasAbertas}`),
  resolver: (pid, id) => api(`/processos/${pid}/pendencias/${id}/resolver`, { metodo: 'POST' }),
}

export const analise = {
  obter: (pid) => api(`/processos/${pid}/analise`),
  executar: (pid) => api(`/processos/${pid}/analise/executar`, { metodo: 'POST' }),
  arvore: (pid) => api(`/processos/${pid}/arvore`),
}
