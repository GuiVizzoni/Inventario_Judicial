export default function ProgressoDocumental({ percentual = 0, rotulo }) {
  return (
    <div>
      {rotulo && (
        <div className="mb-1.5 flex items-baseline justify-between">
          <span className="text-sm text-slate">{rotulo}</span>
          <span className="font-mono text-sm text-ink">{percentual}%</span>
        </div>
      )}
      <div className="h-2 w-full overflow-hidden rounded-full bg-ink/10">
        <div
          className="h-full rounded-full bg-gradient-to-r from-bronze-soft to-bronze"
          style={{ width: `${percentual}%` }}
        />
      </div>
    </div>
  )
}
