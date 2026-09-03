import { Source_Serif_4, Inter, IBM_Plex_Mono } from 'next/font/google'
import './globals.css'
import { SessaoProvider } from '@/components/SessaoProvider'

const serif = Source_Serif_4({
  subsets: ['latin'],
  variable: '--font-serif',
  weight: ['500', '600', '700'],
})

const sans = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
  weight: ['400', '500', '600'],
})

const mono = IBM_Plex_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  weight: ['400', '500'],
})

export const metadata = {
  title: 'Plataforma de Inventário Judicial',
  description: 'Automação e organização documental do procedimento sucessório',
}

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR" className={`${serif.variable} ${sans.variable} ${mono.variable}`}>
      <body>
        <SessaoProvider>{children}</SessaoProvider>
      </body>
    </html>
  )
}
