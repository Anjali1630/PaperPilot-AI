import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  FileText, Sparkles, Lightbulb, AlertTriangle, Rocket, Layers, Tags,
  BookMarked, HelpCircle, PresentationIcon, Quote, Gauge, MessageSquare,
  Download, RefreshCw,
} from 'lucide-react'
import AppLayout from '../components/AppLayout'
import { Loader, Section, StatusBadge } from '../components/UI'
import { getPaper, reanalyzePaper } from '../api/endpoints'
import client from '../api/client'

const TABS = [
  { id: 'summary', label: 'Summary', icon: Sparkles },
  { id: 'contributions', label: 'Contributions & Gaps', icon: Lightbulb },
  { id: 'methodology', label: 'Methodology', icon: Layers },
  { id: 'keywords', label: 'Keywords', icon: Tags },
  { id: 'flashcards', label: 'Flashcards', icon: BookMarked },
  { id: 'viva', label: 'Viva Questions', icon: HelpCircle },
  { id: 'ppt', label: 'PPT Outline', icon: PresentationIcon },
  { id: 'citations', label: 'Citations', icon: Quote },
]

function safeParse(json, fallback) {
  try { return JSON.parse(json || 'null') ?? fallback } catch { return fallback }
}

export default function Analysis() {
  const { id } = useParams()
  const [paper, setPaper] = useState(null)
  const [tab, setTab] = useState('summary')
  const [loading, setLoading] = useState(true)

  const load = () => getPaper(id).then((res) => setPaper(res.data)).finally(() => setLoading(false))

  useEffect(() => { load() }, [id])

  useEffect(() => {
    if (!paper) return
    if (paper.status === 'processing' || paper.status === 'uploaded') {
      const interval = setInterval(load, 4000)
      return () => clearInterval(interval)
    }
  }, [paper?.status])

  if (loading) return <AppLayout title="Analysis"><Loader label="Loading paper..." /></AppLayout>
  if (!paper) return <AppLayout title="Analysis"><p>Paper not found.</p></AppLayout>

  if (paper.status === 'processing' || paper.status === 'uploaded') {
    return (
      <AppLayout title="Analysis">
        <div className="max-w-lg mx-auto text-center py-24">
          <div className="h-14 w-14 mx-auto mb-5 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
          <h2 className="font-bold text-slate-800 dark:text-white text-lg">Analyzing "{paper.filename}"...</h2>
          <p className="text-sm text-slate-500 mt-2">Our local AI models are summarizing, extracting keywords, generating flashcards and more. This can take a minute or two depending on paper length.</p>
        </div>
      </AppLayout>
    )
  }

  if (paper.status === 'failed') {
    return (
      <AppLayout title="Analysis">
        <div className="max-w-lg mx-auto text-center py-24">
          <AlertTriangle size={40} className="mx-auto text-red-500 mb-4" />
          <h2 className="font-bold text-slate-800 dark:text-white text-lg">Analysis Failed</h2>
          <p className="text-sm text-slate-500 mt-2">{paper.error_message}</p>
          <button onClick={() => reanalyzePaper(id).then(load)} className="btn-primary mt-6">
            <RefreshCw size={16} /> Retry Analysis
          </button>
        </div>
      </AppLayout>
    )
  }

  const keywords = safeParse(paper.keywords_json, [])
  const contributions = safeParse(paper.key_contributions, [])
  const gaps = safeParse(paper.research_gaps, [])
  const futureScope = safeParse(paper.future_scope, [])
  const methodology = safeParse(paper.methodology_json, {})
  const flashcards = safeParse(paper.flashcards_json, [])
  const viva = safeParse(paper.viva_questions_json, {})
  const ppt = safeParse(paper.ppt_outline_json, [])
  const citations = safeParse(paper.citations_json, {})
  const authors = safeParse(paper.authors, [])

  return (
    <AppLayout title="Analysis">
      <div className="mb-6 flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-800 dark:text-white">{paper.title || paper.filename}</h1>
          <p className="text-sm text-slate-500 mt-1">{authors.join(', ') || 'Author(s) not detected'}</p>
          <div className="flex items-center gap-2 mt-3 flex-wrap">
            <StatusBadge status={paper.status} />
            <span className="pill"><Gauge size={12} className="mr-1" />{paper.difficulty_label} ({paper.difficulty_score}/100)</span>
            <span className="pill">~{paper.estimated_reading_minutes} min read</span>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Link to={`/papers/${id}/chat`} className="btn-secondary text-sm"><MessageSquare size={15} /> Chat with PDF</Link>
          <ExportMenu paperId={id} />
        </div>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex items-center gap-1.5 whitespace-nowrap rounded-xl px-4 py-2 text-sm font-semibold transition ${
              tab === t.id ? 'bg-brand-600 text-white shadow-md' : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700'
            }`}
          >
            <t.icon size={15} /> {t.label}
          </button>
        ))}
      </div>

      {tab === 'summary' && (
        <div className="grid lg:grid-cols-2 gap-5">
          <Section title="Executive Summary" icon={Sparkles}><p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300 whitespace-pre-line">{paper.executive_summary}</p></Section>
          <Section title="Standard Summary" icon={FileText}><p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300 whitespace-pre-line">{paper.standard_summary}</p></Section>
          <Section title="Detailed Summary" icon={FileText} className="lg:col-span-2"><p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300 whitespace-pre-line">{paper.detailed_summary}</p></Section>
          <Section title="Simplified Technical Explanation" icon={Lightbulb} className="lg:col-span-2"><p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300 whitespace-pre-line">{paper.simplified_explanation}</p></Section>
        </div>
      )}

      {tab === 'contributions' && (
        <div className="grid lg:grid-cols-3 gap-5">
          <Section title="Key Contributions" icon={Lightbulb}>
            <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-300 list-disc pl-4">{contributions.map((c, i) => <li key={i}>{c}</li>)}</ul>
          </Section>
          <Section title="Research Gaps" icon={AlertTriangle}>
            <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-300 list-disc pl-4">{gaps.map((c, i) => <li key={i}>{c}</li>)}</ul>
          </Section>
          <Section title="Future Scope" icon={Rocket}>
            <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-300 list-disc pl-4">{futureScope.map((c, i) => <li key={i}>{c}</li>)}</ul>
          </Section>
        </div>
      )}

      {tab === 'methodology' && (
        <div className="grid lg:grid-cols-2 gap-5">
          <Section title="Algorithms Used"><div className="flex flex-wrap gap-2">{(methodology.algorithms || []).map((a) => <span key={a} className="pill">{a}</span>)}</div></Section>
          <Section title="Datasets"><div className="flex flex-wrap gap-2">{(methodology.datasets || []).map((a) => <span key={a} className="pill">{a}</span>)}</div></Section>
          <Section title="Evaluation Metrics"><div className="flex flex-wrap gap-2">{(methodology.evaluation_metrics || []).map((a) => <span key={a} className="pill">{a}</span>)}</div></Section>
          <Section title="Pipeline Steps">
            <ol className="space-y-2 text-sm text-slate-600 dark:text-slate-300 list-decimal pl-4">{(methodology.pipeline_steps || []).map((s, i) => <li key={i}>{s}</li>)}</ol>
          </Section>
        </div>
      )}

      {tab === 'keywords' && (
        <Section title="Top Keywords">
          <div className="flex flex-wrap gap-2">
            {keywords.map((k) => (
              <span key={k.keyword} className="pill" style={{ fontSize: `${11 + Math.min(k.score * 10, 6)}px` }}>{k.keyword}</span>
            ))}
          </div>
        </Section>
      )}

      {tab === 'flashcards' && (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {flashcards.map((c, i) => <FlipCard key={i} q={c.question} a={c.answer} />)}
        </div>
      )}

      {tab === 'viva' && (
        <div className="space-y-5">
          {Object.entries(viva).map(([level, questions]) => (
            <Section key={level} title={level.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())} icon={HelpCircle}>
              <ol className="space-y-2 text-sm text-slate-600 dark:text-slate-300 list-decimal pl-4">{questions.map((q, i) => <li key={i}>{q}</li>)}</ol>
            </Section>
          ))}
        </div>
      )}

      {tab === 'ppt' && (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {ppt.map((s) => (
            <div key={s.slide_no} className="glass-card p-4">
              <p className="text-xs font-semibold text-brand-600 mb-1">Slide {s.slide_no}</p>
              <p className="font-bold text-slate-800 dark:text-white mb-2">{s.title}</p>
              <ul className="text-xs text-slate-500 space-y-1 list-disc pl-4">{(s.bullets || []).map((b, i) => <li key={i}>{b}</li>)}</ul>
            </div>
          ))}
        </div>
      )}

      {tab === 'citations' && (
        <Section title="Citation Formats" icon={Quote}>
          <div className="space-y-3">
            {Object.entries(citations).map(([style, text]) => (
              <div key={style} className="rounded-xl bg-slate-50 dark:bg-slate-800/60 p-4">
                <p className="text-xs font-bold text-brand-600 uppercase mb-1">{style}</p>
                <p className="text-sm text-slate-700 dark:text-slate-300">{text}</p>
              </div>
            ))}
          </div>
        </Section>
      )}
    </AppLayout>
  )
}

function FlipCard({ q, a }) {
  const [flipped, setFlipped] = useState(false)
  return (
    <div onClick={() => setFlipped(!flipped)} className="glass-card p-5 min-h-[140px] flex items-center justify-center text-center cursor-pointer select-none hover:shadow-glow transition">
      <p className={`text-sm ${flipped ? 'text-emerald-600 dark:text-emerald-400 font-medium' : 'text-slate-700 dark:text-slate-200 font-semibold'}`}>
        {flipped ? a : q}
      </p>
    </div>
  )
}

function ExportMenu({ paperId }) {
  const [open, setOpen] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const formats = [
    { id: 'pdf', label: 'PDF Report' },
    { id: 'docx', label: 'Word (.docx)' },
    { id: 'pptx', label: 'PowerPoint (.pptx)' },
    { id: 'md', label: 'Markdown' },
    { id: 'txt', label: 'Plain Text' },
  ]

  const handleExport = async (fmt) => {
    setOpen(false)
    setDownloading(true)
    try {
      const res = await client.get(`/papers/${paperId}/export/${fmt}`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      const disposition = res.headers['content-disposition'] || ''
      const match = disposition.match(/filename="?([^"]+)"?/)
      link.download = match ? match[1] : `paper.${fmt}`
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      alert('Export failed. Please try again.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="relative">
      <button onClick={() => setOpen(!open)} disabled={downloading} className="btn-primary text-sm">
        <Download size={15} /> {downloading ? 'Exporting...' : 'Export'}
      </button>
      {open && (
        <div className="absolute right-0 mt-2 w-48 glass-card p-2 z-20">
          {formats.map((f) => (
            <button
              key={f.id}
              onClick={() => handleExport(f.id)}
              className="block w-full text-left px-3 py-2 rounded-lg text-sm text-slate-700 dark:text-slate-200 hover:bg-brand-50 dark:hover:bg-brand-900/30"
            >
              {f.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
