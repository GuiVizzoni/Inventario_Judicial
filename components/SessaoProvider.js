'use client'

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { auth, limparSessao, obterToken, processos as apiProcessos, salvarSessao } from '@/lib/api'

const SessaoContexto = createContext(null)

export function SessaoProvider({ children }) {
  const router = useRouter()
  const pathname = usePathname()
  const [usuario, setUsuario] = useState(null)
  const [lista, setLista] = useState([])
  const [processoId, setProcessoIdInterno] = useState(null)
  const [carregando, setCarregando] = useState(true)

  const escolherProcesso = useCallback((id) => {
    setProcessoIdInterno(id)
    try {
      if (id) localStorage.setItem('processoId', id)
      else localStorage.removeItem('processoId')
    } catch {}
  }, [])

  const carregarProcessos = useCallback(async (preferido) => {
    const processos = await apiProcessos.listar()
    setLista(processos)
    let salvo = preferido || null
    if (!salvo) {
      try {
        salvo = localStorage.getItem('processoId')
      } catch {}
    }
    const existe = processos.find((p) => p.id === salvo)
    escolherProcesso(existe ? salvo : processos[0] ? processos[0].id : null)
    return processos
  }, [escolherProcesso])

  useEffect(() => {
    const token = obterToken()
    if (!token) {
      setCarregando(false)
      if (pathname !== '/login') router.replace('/login')
      return
    }
    let ativo = true
    ;(async () => {
      try {
        const me = await auth.me()
        if (!ativo) return
        setUsuario(me)
        await carregarProcessos()
      } catch {
        limparSessao()
        if (ativo && pathname !== '/login') router.replace('/login')
      } finally {
        if (ativo) setCarregando(false)
      }
    })()
    return () => {
      ativo = false
    }
  }, [])

  const entrar = useCallback(async (email, senha) => {
    const resposta = await auth.login(email, senha)
    salvarSessao(resposta.access_token)
    setUsuario(resposta.usuario)
    await carregarProcessos()
  }, [carregarProcessos])

  const sair = useCallback(() => {
    limparSessao()
    setUsuario(null)
    setLista([])
    setProcessoIdInterno(null)
    router.replace('/login')
  }, [router])

  const processo = useMemo(() => lista.find((p) => p.id === processoId) || null, [lista, processoId])

  const valor = useMemo(
    () => ({ usuario, lista, processo, processoId, carregando, entrar, sair, escolherProcesso, carregarProcessos }),
    [usuario, lista, processo, processoId, carregando, entrar, sair, escolherProcesso, carregarProcessos]
  )

  return <SessaoContexto.Provider value={valor}>{children}</SessaoContexto.Provider>
}

export function useSessao() {
  const contexto = useContext(SessaoContexto)
  if (!contexto) throw new Error('useSessao deve ser usado dentro de SessaoProvider')
  return contexto
}
