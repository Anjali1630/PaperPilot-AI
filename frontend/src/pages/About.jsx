import { Link } from 'react-router-dom'
import { BrainCircuit, Github, ArrowLeft } from 'lucide-react'

const stack = [
  { group: 'Frontend', items: ['React', 'Vite', 'Tailwind CSS', 'Framer Motion', 'Recharts'] },
  { group: 'Backend', items: ['FastAPI', 'Python 3.11', 'SQLite', 'SQLAlchemy'] },
  { group: 'AI / NLP (100% local & free)', items: ['HuggingFace Transformers (BART)', 'Sentence-Transformers', 'KeyBERT', 'spaCy', 'FAISS'] },
  { group: 'Export', items: ['python-docx', 'python-pptx', 'ReportLab'] },
]

export default function About() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-brand-50/40 dark:from-slate-950 dark:to-slate-900 px-6 py-10">
      <div className="max-w-3xl mx-auto">
        <Link to="/" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-brand-600 mb-8">
          <ArrowLeft size={16} /> Back home
        </Link>

        <div className="flex items-center gap-3 mb-6">
          <div className="h-11 w-11 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-glow">
            <BrainCircuit className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-3xl font-extrabold text-slate-800 dark:text-white">About PaperPilot AI</h1>
        </div>

        <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-6">
          PaperPilot AI is an AI-powered research paper summarizer and academic assistant built as a
          final-year AIML major project. It helps students, researchers, and professors quickly
          understand research papers by generating summaries, simplified explanations, key
          contributions, research gaps, methodology breakdowns, flashcards, viva questions, citations,
          and more — entirely using free, open-source, locally-run AI models. No paid API keys are
          required to run this project.
        </p>

        <div className="grid sm:grid-cols-2 gap-4 mb-8">
          {stack.map((s) => (
            <div key={s.group} className="glass-card p-4">
              <p className="text-xs font-bold uppercase text-brand-600 mb-2">{s.group}</p>
              <ul className="text-sm text-slate-600 dark:text-slate-300 space-y-1">
                {s.items.map((i) => <li key={i}>• {i}</li>)}
              </ul>
            </div>
          ))}
        </div>

        <div className="glass-card p-5">
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Built for academic and placement-interview demonstration purposes. See the project README
            for full setup instructions, architecture diagram, and API documentation.
          </p>
        </div>
      </div>
    </div>
  )
}
