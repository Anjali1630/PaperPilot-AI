import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FileText, CheckCircle2, Clock, TrendingUp, ArrowUpRight } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import AppLayout from '../components/AppLayout'
import { StatCard, Loader, StatusBadge, Section, EmptyState } from '../components/UI'
import { getDashboard } from '../api/endpoints'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDashboard().then((res) => setData(res.data)).finally(() => setLoading(false))
  }, [])

  return (
    <AppLayout title="Dashboard">
      <div className="mb-6">
        <h1 className="text-2xl font-extrabold text-slate-800 dark:text-white">Dashboard</h1>
        <p className="text-sm text-slate-500">Your research analysis activity at a glance.</p>
      </div>

      {loading && <Loader label="Loading your dashboard..." />}

      {!loading && data && (
        <div className="space-y-6">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard icon={FileText} label="Papers Uploaded" value={data.total_papers} />
            <StatCard icon={CheckCircle2} label="Papers Summarized" value={data.papers_summarized} accent="emerald" />
            <StatCard icon={Clock} label="Avg. Minutes Saved / Paper" value={data.avg_reading_minutes_saved} accent="amber" />
            <StatCard icon={TrendingUp} label="Top Keywords Tracked" value={data.top_keywords.length} accent="purple" />
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            <Section title="Frequently Used Keywords" className="lg:col-span-2">
              {data.top_keywords.length === 0 ? (
                <p className="text-sm text-slate-500 py-10 text-center">Upload and analyze papers to see keyword trends.</p>
              ) : (
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={data.top_keywords} margin={{ top: 5, right: 10, left: -20, bottom: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="keyword" angle={-35} textAnchor="end" interval={0} height={70} tick={{ fontSize: 11 }} />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#6366f1" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </Section>

            <Section title="Recent Activity">
              {data.recent_activity.length === 0 ? (
                <p className="text-sm text-slate-500 py-10 text-center">No activity yet.</p>
              ) : (
                <ul className="space-y-3 max-h-72 overflow-y-auto pr-1">
                  {data.recent_activity.map((a) => (
                    <li key={`${a.paper_id}-${a.timestamp}`} className="flex items-center justify-between gap-2">
                      <Link to={`/papers/${a.paper_id}`} className="text-sm font-medium text-slate-700 dark:text-slate-200 hover:text-brand-600 truncate">
                        {a.title}
                      </Link>
                      <StatusBadge status={a.status} />
                    </li>
                  ))}
                </ul>
              )}
            </Section>
          </div>

          <Section title="Recent Uploads">
            {data.recent_uploads.length === 0 ? (
              <EmptyState
                icon={FileText}
                title="No papers yet"
                subtitle="Upload your first research paper PDF to get started."
                action={<Link to="/upload" className="btn-primary">Upload a Paper</Link>}
              />
            ) : (
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {data.recent_uploads.map((p) => (
                  <Link key={p.id} to={`/papers/${p.id}`} className="rounded-xl border border-slate-200 dark:border-slate-800 p-4 hover:shadow-md hover:border-brand-300 transition group">
                    <div className="flex items-start justify-between">
                      <p className="font-semibold text-sm text-slate-800 dark:text-white line-clamp-2 pr-2">{p.title || p.filename}</p>
                      <ArrowUpRight size={16} className="text-slate-400 group-hover:text-brand-600 shrink-0" />
                    </div>
                    <div className="mt-3 flex items-center justify-between">
                      <StatusBadge status={p.status} />
                      {p.difficulty_label && <span className="pill">{p.difficulty_label}</span>}
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </Section>
        </div>
      )}
    </AppLayout>
  )
}
