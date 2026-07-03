import { motion } from 'framer-motion'

export function StatCard({ icon: Icon, label, value, accent = 'brand' }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5 flex items-center gap-4"
    >
      <div className={`h-12 w-12 rounded-xl bg-${accent}-100 dark:bg-${accent}-900/40 flex items-center justify-center text-${accent}-600 dark:text-${accent}-300`}>
        <Icon size={22} />
      </div>
      <div>
        <p className="text-2xl font-extrabold text-slate-800 dark:text-white">{value}</p>
        <p className="text-xs font-medium text-slate-500 dark:text-slate-400">{label}</p>
      </div>
    </motion.div>
  )
}

export function Loader({ label = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3 text-slate-500">
      <div className="h-9 w-9 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
      <p className="text-sm">{label}</p>
    </div>
  )
}

export function StatusBadge({ status }) {
  const styles = {
    uploaded: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300',
    processing: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300 animate-pulse',
    analyzed: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300',
    failed: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
  }
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${styles[status] || styles.uploaded}`}>
      {status}
    </span>
  )
}

export function EmptyState({ icon: Icon, title, subtitle, action }) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-20 glass-card">
      {Icon && <Icon size={40} className="text-brand-300 mb-3" />}
      <p className="font-semibold text-slate-700 dark:text-slate-200">{title}</p>
      {subtitle && <p className="text-sm text-slate-500 mt-1 max-w-sm">{subtitle}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

export function Section({ title, icon: Icon, children, className = '' }) {
  return (
    <div className={`glass-card p-5 sm:p-6 ${className}`}>
      <h3 className="section-title mb-3">
        {Icon && <Icon size={18} className="text-brand-600" />}
        {title}
      </h3>
      {children}
    </div>
  )
}
