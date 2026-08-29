/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,jsx}',
    './components/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: '#101827',
          soft: '#1C2A3F',
        },
        parchment: {
          DEFAULT: '#F7F3EA',
          deep: '#EDE6D6',
        },
        bronze: {
          DEFAULT: '#A8823C',
          soft: '#C7A46B',
          dark: '#8A6A2E',
        },
        slate: {
          DEFAULT: '#4B5563',
        },
        selo: {
          success: '#2F6B4F',
          warning: '#B7791F',
          danger: '#B3492B',
          neutral: '#6B7280',
        },
      },
      fontFamily: {
        display: ['var(--font-serif)', 'serif'],
        body: ['var(--font-sans)', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      backgroundImage: {
        'paper-grain': "radial-gradient(circle at 1px 1px, rgba(16,24,39,0.035) 1px, transparent 0)",
      },
      backgroundSize: {
        'paper-grain': '18px 18px',
      },
    },
  },
  plugins: [],
}
