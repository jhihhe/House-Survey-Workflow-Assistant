import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

requestAnimationFrame(() => {
  const splash = document.getElementById('boot-splash')
  if (!splash) return
  splash.classList.add('hide')
  window.setTimeout(() => splash.remove(), 320)
})
