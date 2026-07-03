import { Link } from 'react-router-dom'
import { FileQuestion } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-slate-50 via-white to-brand-50/40 dark:from-slate-950 dark:to-slate-900 text-center px-6">
      <FileQuestion size={56} className="text-brand-300 mb-4" />
      <h1 className="text-4xl font-extrabold text-slate-800 dark:text-white mb-2">404</h1>
      <p className="text-slate-500 mb-6">This page doesn't exist.</p>
      <Link to="/" className="btn-primary">Go Home</Link>
    </div>
  )
}
