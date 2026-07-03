import { Menu } from 'lucide-react'
import { useState } from 'react'
import { NavLink } from 'react-router-dom'

export default function Topbar({ title }) {
  const [open, setOpen] = useState(false)

  return (
    <div className="lg:hidden sticky top-0 z-30 flex items-center justify-between border-b border-slate-200 dark:border-slate-800 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md px-4 py-3">
      <span className="font-bold text-slate-800 dark:text-white">{title || 'PaperPilot.AI'}</span>
      <button onClick={() => setOpen(!open)} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800">
        <Menu size={20} />
      </button>
      {open && (
        <div className="absolute top-full left-0 w-full bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-lg p-3 flex flex-col gap-1">
          {['dashboard', 'upload', 'history', 'compare', 'settings'].map((p) => (
            <NavLink key={p} to={`/${p}`} onClick={() => setOpen(false)} className="px-3 py-2 rounded-lg text-sm font-medium capitalize hover:bg-slate-100 dark:hover:bg-slate-800">
              {p}
            </NavLink>
          ))}
        </div>
      )}
    </div>
  )
}
