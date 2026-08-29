import Navbar from '@/components/Navbar'
import Card from '@/components/Card'

function No({ nome, papel, raiz = false }) {
  return (
    <div
      className={`flex w-40 flex-col items-center rounded-sm border px-3 py-2.5 text-center ${
        raiz ? 'border-bronze bg-bronze/10' : 'border-ink/15 bg-white'
      }`}
    >
      <p className="text-xs font-medium leading-tight text-ink">{nome}</p>
      <p className="mt-0.5 text-[10px] uppercase tracking-wide text-slate">{papel}</p>
    </div>
  )
}

export default function ArvoreGenealogica() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <p className="font-mono text-xs uppercase tracking-widest text-bronze-dark">
          Relações familiares
        </p>
        <h1 className="mt-1 font-display text-3xl font-semibold text-ink">
          Árvore Genealógica Automatizada
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-slate">
          Representação gerada a partir das certidões e informações cadastradas,
          evidenciando as relações relevantes para a sucessão patrimonial.
        </p>

        <Card className="mt-8 overflow-x-auto">
          <div className="flex min-w-[640px] flex-col items-center gap-8 py-6">
            {/* De cujus + cônjuge */}
            <div className="flex items-center gap-6">
              <No nome="Roberto Mendes da Silva" papel="De cujus" raiz />
              <span className="text-slate">+</span>
              <No nome="Marta Aparecida Silva" papel="Cônjuge" />
            </div>

            {/* Linha conectora */}
            <div className="h-8 w-px bg-ink/20" />
            <div className="h-px w-[520px] bg-ink/20" />

            {/* Filhos */}
            <div className="flex gap-10">
              {['Carlos Mendes da Silva', 'Juliana Mendes Ribeiro', 'Pedro Henrique Mendes'].map((nome) => (
                <div key={nome} className="flex flex-col items-center gap-3">
                  <div className="h-6 w-px bg-ink/20" />
                  <No nome={nome} papel="Filho(a)" />
                </div>
              ))}
            </div>
          </div>
        </Card>

        <Card className="mt-6" title="Observações da análise automatizada">
          <ul className="space-y-2 text-sm text-slate">
            <li>• Filiação confirmada por certidão de nascimento para os 3 herdeiros diretos.</li>
            <li>• Não foram identificados indícios de outros herdeiros necessários.</li>
            <li>• Regime de bens do casamento: comunhão parcial (confirmado por certidão).</li>
          </ul>
        </Card>
      </main>
    </div>
  )
}
