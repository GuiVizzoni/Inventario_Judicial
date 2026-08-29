export default function Card({ children, className = '', title, eyebrow, action }) {
  return (
    <div className={`rounded-md border border-ink/10 bg-white/70 p-6 shadow-[0_1px_2px_rgba(16,24,39,0.04)] ${className}`}>
      {(title || eyebrow || action) && (
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            {eyebrow && (
              <p className="mb-1 font-mono text-[11px] uppercase tracking-wider text-bronze-dark">
                {eyebrow}
              </p>
            )}
            {title && <h3 className="font-display text-lg font-semibold text-ink">{title}</h3>}
          </div>
          {action}
        </div>
      )}
      {children}
    </div>
  )
}
