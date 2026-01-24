/**
 * Application Entry Point
 * Renders React app into the DOM
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './pages/App'
import { ThemeProvider } from './contexts/ThemeContext'
import './styles/globals.css'
import 'react-datepicker/dist/react-datepicker.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>,
)
