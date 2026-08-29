# Plataforma de Inventário Judicial — Protótipo de Telas

Protótipo navegável em **Next.js 14 (App Router) + React + Tailwind CSS**,
implementando as 9 telas previstas na proposta do TCC sobre automação do
inventário judicial:

1. Login
2. Central do Inventário
3. Cadastro Inicial do Inventário
4. Checklist Documental
5. Gerenciamento de Documentos
6. Gestão de Herdeiros
7. Gestão Patrimonial
8. Árvore Genealógica Automatizada
9. Análise Inteligente do Inventário (IA)

Os dados exibidos são **mockados** (fictícios), definidos diretamente no
código de cada página — não há backend nem banco de dados conectado. O
objetivo é validar fluxos de navegação e organização visual, conforme
descrito na seção de protótipos do TCC.

## Identidade visual

- **Cores**: tons de tinta/navy (`ink`), papel (`parchment`) e bronze,
  remetendo a documentos e selos cartorários.
- **Tipografia**: Source Serif 4 (títulos), Inter (texto/UI) e IBM Plex Mono
  (números de processo, códigos, valores).
- **Selo**: componente de badge reutilizado em todas as telas para indicar
  status de documentos, herdeiros e bens (Concluído, Em análise, Pendente,
  Rejeitado, Não iniciado).

## Pré-requisitos

- [Node.js](https://nodejs.org/) versão 18.18 ou superior
- npm (instalado junto com o Node.js)

Para conferir sua versão:

```bash
node -v
npm -v
```

## Passo a passo para rodar localmente

1. **Extraia** o arquivo `.zip` recebido em uma pasta de sua preferência.

2. **Abra o terminal** dentro da pasta do projeto:

   ```bash
   cd inventario-judicial
   ```

3. **Instale as dependências:**

   ```bash
   npm install
   ```

4. **Rode o servidor de desenvolvimento:**

   ```bash
   npm run dev
   ```

5. **Acesse no navegador:**

   ```
   http://localhost:3000
   ```

   A rota inicial (`/`) redireciona automaticamente para `/login`.

## Rotas disponíveis

| Tela                              | Rota                       |
|-----------------------------------|----------------------------|
| Login                              | `/login`                   |
| Central do Inventário              | `/central`                 |
| Cadastro Inicial do Inventário      | `/inventario/novo`         |
| Checklist Documental                | `/documentos/checklist`    |
| Gerenciamento de Documentos          | `/documentos`              |
| Gestão de Herdeiros                 | `/herdeiros`               |
| Gestão Patrimonial                  | `/patrimonio`              |
| Árvore Genealógica Automatizada      | `/arvore-genealogica`      |
| Análise Inteligente do Inventário    | `/analise-ia`              |

O menu horizontal no topo (visível a partir da tela de Login → Central)
permite navegar entre os módulos, como descrito no fluxo de navegação do TCC.

## Estrutura do projeto

```
inventario-judicial/
├── app/
│   ├── layout.js              # Layout raiz (fontes + metadata)
│   ├── globals.css            # Estilos globais + Tailwind
│   ├── page.js                # Redireciona para /login
│   ├── login/page.js
│   ├── central/page.js
│   ├── inventario/novo/page.js
│   ├── documentos/page.js
│   ├── documentos/checklist/page.js
│   ├── herdeiros/page.js
│   ├── patrimonio/page.js
│   ├── arvore-genealogica/page.js
│   └── analise-ia/page.js
├── components/
│   ├── Navbar.js               # Menu horizontal persistente
│   ├── Card.js                 # Container padrão de conteúdo
│   ├── Selo.js                 # Badge de status (elemento de assinatura visual)
│   └── ProgressoDocumental.js  # Barra de progresso
├── tailwind.config.js
├── postcss.config.js
├── next.config.js
├── jsconfig.json
└── package.json
```

## Build de produção (opcional)

```bash
npm run build
npm run start
```

## Próximos passos sugeridos (fora do escopo deste protótipo)

- Conectar autenticação real (NextAuth ou similar) na tela de Login.
- Substituir os dados mockados por chamadas a uma API/backend.
- Persistir uploads de documentos e status em um banco de dados.
- Integrar o painel de Análise IA a um serviço real de extração/validação
  documental.
