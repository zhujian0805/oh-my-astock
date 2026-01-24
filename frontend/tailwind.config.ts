/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Roboto', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#e8f0fe',
          100: '#d2e3fc',
          500: '#1a73e8', // Google Blue
          600: '#1967d2',
          700: '#185abc',
        },
        gray: {
          50: '#f8f9fa',
          100: '#f1f3f4',
          200: '#e8eaed',
          300: '#dadce0',
          400: '#bdc1c6',
          500: '#9aa0a6',
          600: '#80868b',
          700: '#5f6368',
          800: '#3c4043',
          900: '#202124',
        },
        success: {
          500: '#1e8e3e',
          600: '#137333',
        },
        danger: {
          500: '#d93025',
          600: '#c5221f',
        },
        warning: {
          500: '#f9ab00',
          600: '#e37400',
        }
      },
      spacing: {
        '128': '32rem',
      },
      borderRadius: {
        'lg': '8px',
      }
    },
  },
  plugins: [],
  darkMode: 'class',
}
