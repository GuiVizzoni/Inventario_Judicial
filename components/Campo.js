export function Campo({ label, tipo = 'text', valor, aoMudar, placeholder, obrigatorio = false, className = '' }) {
  return (
    <div className={className}>
      <label className="mb-1.5 block text-sm font-medium text-ink">{label}</label>
      <input
        type={tipo}
        value={valor ?? ''}
        onChange={(e) => aoMudar(e.target.value)}
        placeholder={placeholder}
        required={obrigatorio}
        className="w-full rounded-sm border border-ink/15 bg-white px-3 py-2.5 text-sm text-ink placeholder:text-slate/50 focus:border-bronze"
      />
    </div>
  )
}

export function Selecao({ label, valor, aoMudar, opcoes, className = '' }) {
  return (
    <div className={className}>
      <label className="mb-1.5 block text-sm font-medium text-ink">{label}</label>
      <select
        value={valor ?? ''}
        onChange={(e) => aoMudar(e.target.value)}
        className="w-full rounded-sm border border-ink/15 bg-white px-3 py-2.5 text-sm text-ink focus:border-bronze"
      >
        {opcoes.map((o) => (
          <option key={o.valor} value={o.valor}>
            {o.rotulo}
          </option>
        ))}
      </select>
    </div>
  )
}

export function Alerta({ mensagem, tipo = 'erro' }) {
  if (!mensagem) return null
  const cor = tipo === 'erro' ? 'border-selo-danger/40 bg-selo-danger/5 text-selo-danger' : 'border-selo-success/40 bg-selo-success/5 text-selo-success'
  return <p className={`rounded-sm border px-3 py-2 text-sm ${cor}`}>{mensagem}</p>
}

export function BotaoPrimario({ children, carregando = false, ...props }) {
  return (
    <button
      type="submit"
      disabled={carregando || props.disabled}
      {...props}
      className={`rounded-sm bg-ink px-4 py-2.5 text-sm font-medium text-parchment transition-colors hover:bg-ink-soft disabled:opacity-60 ${props.className || ''}`}
    >
      {children}
    </button>
  )
}

export function BotaoSecundario({ children, ...props }) {
  return (
    <button
      type="button"
      {...props}
      className={`rounded-sm border border-ink/15 px-4 py-2.5 text-sm font-medium text-ink hover:bg-ink/5 disabled:opacity-60 ${props.className || ''}`}
    >
      {children}
    </button>
  )
}
