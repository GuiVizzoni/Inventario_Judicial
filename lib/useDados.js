'use client'

import { useCallback, useEffect, useState } from 'react'

export function useDados(carregador, dependencias) {
  const [dados, setDados] = useState(null)
  const [erro, setErro] = useState(null)
  const [carregando, setCarregando] = useState(true)

  const recarregar = useCallback(async () => {
    setErro(null)
    try {
      const resultado = await carregador()
      setDados(resultado)
      return resultado
    } catch (e) {
      setErro(e.message)
      return null
    } finally {
      setCarregando(false)
    }
  }, dependencias)

  useEffect(() => {
    setCarregando(true)
    recarregar()
  }, [recarregar])

  return { dados, erro, carregando, recarregar, setDados }
}
