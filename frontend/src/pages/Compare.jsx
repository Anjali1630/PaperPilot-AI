import { useEffect, useState } from 'react'
import { GitCompareArrows, CheckSquare, Square, Loader2 } from 'lucide-react'
import AppLayout from '../components/AppLayout'
import { Loader, EmptyState, Section } from '../components/UI'
import { listPapers, comparePapers } from '../api/endpoints'

export default function Compare() {
  const [papers, setPapers] = useState([])
  const [selected, setSelected] = useState([])
  const [loading, setLoading] = useState(true)
  const [comparing, setComparing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    listPapers().then((res) => setPapers(res.data.filter((p) => p.is_analyzed))).finally(() => setLoading(false))
  }, [])

  const toggle = (id) => {
    setSelected((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id)
      if (prev.length >= 5) return prev
      return [...prev, id]
    })
  }

  const runCompare = async () => {
    setError('')
    setComparing(true)
    setResult(null)
    try {
      const res = await comparePapers(selected)
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Comparison failed.')
    } finally {
      setComparing(false)
    }
  }

  return (
    <AppLayout title="Compare Papers">
      <div className="mb-6">
        <h1 className="text-2xl font-extrabold text-slate-800 dark:text-white flex items-center gap-2">
          <GitCompareArrows className="text-brand-600" /> Compare Research Papers
        </h1>
        <p className="text-sm text-slate-500">Select 2–5 analyzed papers to compare methodology, datasets, and findings.</p>
      </div>

      {loading && <Loader label="Loading your papers..." />}

      {!loading && papers.length < 2 && (
        <EmptyState icon={GitCompareArrows} title="Not enough analyzed papers yet" subtitle="Upload and analyze at least 2 papers to use comparison." />
      )}

      {!loading && papers.length >= 2 && (
        <>
          <Section title={`Select Papers (${selected.length}/5)`} className="mb-6">
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {papers.map((p) => {
                const isSelected = selected.includes(p.id)
                return (
                  <button
                    key={p.id}
                    onClick={() => toggle(p.id)}
                    className={`text-left rounded-xl border p-3 transition flex items-start gap-2 ${
                      isSelected ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20' : 'border-slate-200 dark:border-slate-800 hover:border-brand-300'
                    }`}
                  >
                    {isSelected ? <CheckSquare size={18} className="text-brand-600 shrink-0 mt-0.5" /> : <Square size={18} className="text-slate-400 shrink-0 mt-0.5" />}
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-200 line-clamp-2">{p.title || p.filename}</span>
                  </button>
                )
              })}
            </div>
            <div className="mt-4 flex items-center gap-3">
              <button disabled={selected.length < 2 || comparing} onClick={runCompare} className="btn-primary">
                {comparing ? <Loader2 size={16} className="animate-spin" /> : <GitCompareArrows size={16} />}
                Compare {selected.length >= 2 ? `(${selected.length})` : ''}
              </button>
              {error && <span className="text-sm text-red-500">{error}</span>}
            </div>
          </Section>

          {result && <ComparisonResults result={result} />}
        </>
      )}
    </AppLayout>
  )
}

function ComparisonResults({ result }) {
  return (
    <div className="space-y-6">
      <Section title="Comparison Table">
        <div className="overflow-x-auto">
          <table className="w-full text-sm min-w-[720px]">
            <thead className="text-left text-xs uppercase text-slate-500 border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="py-2 pr-4">Paper</th>
                <th className="py-2 pr-4">Algorithms</th>
                <th className="py-2 pr-4">Datasets</th>
                <th className="py-2 pr-4">Metrics</th>
                <th className="py-2 pr-4">Difficulty</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {result.papers.map((p) => (
                <tr key={p.paper_id}>
                  <td className="py-3 pr-4 font-medium text-slate-800 dark:text-white max-w-[220px]">{p.title}</td>
                  <td className="py-3 pr-4 text-slate-600 dark:text-slate-300">{p.algorithms.join(', ') || '—'}</td>
                  <td className="py-3 pr-4 text-slate-600 dark:text-slate-300">{p.datasets.join(', ') || '—'}</td>
                  <td className="py-3 pr-4 text-slate-600 dark:text-slate-300">{p.evaluation_metrics.join(', ') || '—'}</td>
                  <td className="py-3 pr-4"><span className="pill">{p.difficulty_label || 'N/A'}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>

      <div className="grid lg:grid-cols-2 gap-6">
        <Section title="Common Objective Terms">
          {result.common_objective_terms.length === 0 ? (
            <p className="text-sm text-slate-500">No strong overlap detected between abstracts.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {result.common_objective_terms.map((t) => <span key={t} className="pill">{t}</span>)}
            </div>
          )}
        </Section>

        <Section title="Union of Evaluation Metrics">
          <div className="flex flex-wrap gap-2">
            {result.metric_union.length ? result.metric_union.map((m) => <span key={m} className="pill">{m}</span>) : <p className="text-sm text-slate-500">None detected.</p>}
          </div>
        </Section>
      </div>

      {result.papers.map((p) => (
        <Section key={p.paper_id} title={`${p.title} — Gaps & Future Directions`}>
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-bold uppercase text-slate-500 mb-2">Research Gaps</p>
              <ul className="list-disc list-inside text-sm text-slate-600 dark:text-slate-300 space-y-1">
                {p.research_gaps.length ? p.research_gaps.map((g, i) => <li key={i}>{g}</li>) : <li className="list-none text-slate-400">None detected.</li>}
              </ul>
            </div>
            <div>
              <p className="text-xs font-bold uppercase text-slate-500 mb-2">Future Directions</p>
              <ul className="list-disc list-inside text-sm text-slate-600 dark:text-slate-300 space-y-1">
                {p.future_directions.length ? p.future_directions.map((g, i) => <li key={i}>{g}</li>) : <li className="list-none text-slate-400">None detected.</li>}
              </ul>
            </div>
          </div>
        </Section>
      ))}
    </div>
  )
}
