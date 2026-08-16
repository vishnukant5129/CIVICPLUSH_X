/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        civic: {
          50: '#f0f5ff',
          100: '#e5edff',
          200: '#cddbfe',
          300: '#a4bdfc',
          400: '#7695fa',
          500: '#4e6cf3',
          600: '#354ae7',
          700: '#2a39c6',
          800: '#2631a0',
          900: '#232e7f',
          950: '#151a4b',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
