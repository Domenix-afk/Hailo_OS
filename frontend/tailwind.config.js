/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#131313',
        surface: '#131313',
        'surface-variant': '#353534',
        primary: '#e1fdff',
        'primary-dim': '#00dbe7',
        secondary: '#dcb8ff',
        border: '#3a494b',
      },
      fontFamily: {
        sans: ['Geist', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
