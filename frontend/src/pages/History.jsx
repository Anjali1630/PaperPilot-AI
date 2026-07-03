import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Search, Trash2, RefreshCw, FileText, ArrowUpRight } from 'lucide-react'
import AppLayout from '../components/AppLayout'
import { Loader, StatusBadge, EmptyState } from '../components/UI'
import { listPapers, deletePaper, reanalyzePaper } from '../api/endpoints'

export default function HistoryPage() {
  const [papers, setPapers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [busyId, setBusyId] = useState(null)

  const load = (q = '') => {
    setLoading(true)
    listPapers(q).then((res) => setPapers(res.data)).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  useEffect(() => {
    const t = setTimeout(() => load(search), 350)
    return () => clearTimeout(t)
  }, [search])

  const handleDelete = async (id) => {
    if (!confirm('Delete this paper and all its analysis data? This cannot be undone.')) return
    setBusyId(id)
    try {
      await deletePaper(id)
      setPapers((prev) => prev.filter((p) => p.id !== id))
    } finally {
      setBusyId(null)
    }
  }

  const handleReanalyze = async (id) => {
    setBusyId(id)
    try {
      const res = await reanalyzePaper(id)
      setPapers((prev) => prev.map((p) => (p.id === id ? res.data : p)))
    } finally {
      setBusyId(null)
    }
  }

  const filtered = papers.filter((p) => statusFilter === 'all' || p.status === statusFilter)

  return (
    <AppLayout title="History">
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-800 dark:text-white">Upload History</h1>
          <p className="text-sm text-slate-500">Search, filter, re-analyze, or remove your uploaded papers.</p>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by title or filename..."
              className="input-field pl-9 w-64"
            />
          </div>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="input-field w-40">
            <option value="all">All statuses</option>
            <option value="uploaded">Uploaded</option>
            <option value="processing">Processing</option>
            <option value="analyzed">Analyzed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {loading && <Loader label="Loading history..." />}

      {!loading && filtered.length === 0 && (
        <EmptyState icon={FileText} title="No papers found" subtitle="Try a different search or upload a new paper." />
      )}

      {!loading && filtered.length > 0 && (
        <div className="glass-card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 dark:bg-slate-800/50 text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="px-5 py-3">Title</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3">Difficulty</th>
                <th className="px-5 py-3">Uploaded</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {filtered.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                  <td className="px-5 py-3 max-w-xs">
                    <Link to={`/papers/${p.id}`} className="font-medium text-slate-800 dark:text-white hover:text-brand-600 flex items-center gap-1.5 truncate">
                      {p.title || p.filename} <ArrowUpRight size={14} className="shrink-0 text-slate-400" />
                    </Link>
                  </td>
                  <td className="px-5 py-3"><StatusBadge status={p.status} /></td>
                  <td className="px-5 py-3 text-slate-600 dark:text-slate-300">{p.difficulty_label || '—'}</td>
                  <td className="px-5 py-3 text-slate-500">{new Date(p.created_at).toLocaleDateString()}</td>
                  <td className="px-5 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        disabled={busyId === p.id}
                        onClick={() => handleReanalyze(p.id)}
                        className="p-2 rounded-lg text-slate-500 hover:text-brand-600 hover:bg-brand-50 dark:hover:bg-brand-900/30 disabled:opacity-40"
                        title="Re-analyze"
                      >
                        <RefreshCw size={16} className={busyId === p.id ? 'animate-spin' : ''} />
                      </button>
                      <button
                        disabled={busyId === p.id}
                        onClick={() => handleDelete(p.id)}
                        className="p-2 rounded-lg text-slate-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 disabled:opacity-40"
                        title="Delete"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </AppLayout>
  )
}
