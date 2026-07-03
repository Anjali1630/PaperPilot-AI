import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  BrainCircuit, FileText, MessageSquare, GitCompareArrows, Sparkles,
  Layers, Download, ShieldCheck, ArrowRight,
} from 'lucide-react'

const features = [
  { icon: FileText, title: 'Deep Paper Analysis', desc: 'Executive, standard & detailed summaries, key contributions, gaps and future scope — extracted automatically.' },
  { icon: MessageSquare, title: 'Chat With Your PDF', desc: 'Ask questions in plain English and get grounded answers retrieved directly from the paper (local RAG).' },
  { icon: GitCompareArrows, title: 'Compare Papers', desc: 'Upload 2-5 papers and get side-by-side methodology, dataset and performance comparisons.' },
  { icon: Layers, title: 'Study Tools', desc: 'Auto-generated flashcards, viva questions (easy → professor level), and PPT outlines for presentations.' },
  { icon: Download, title: 'Export Anywhere', desc: 'Download full reports as PDF, DOCX, Markdown, TXT or a ready-made PowerPoint deck.' },
  { icon: ShieldCheck, title: '100% Free & Local', desc: 'Runs on open-source Hugging Face models — no OpenAI, no Gemini, no paid API keys, ever.' },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-950 dark:to-slate-900 overflow-hidden">
      <nav className="max-w-7xl mx-auto flex items-center justify-between px-6 py-5">
        <div className="flex items-center gap-2">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-glow">
            <BrainCircuit className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-extrabold text-slate-800 dark:text-white">PaperPilot<span className="text-brand-600">.AI</span></span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/about" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-brand-600">About</Link>
          <Link to="/login" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-brand-600">Log in</Link>
          <Link to="/register" className="btn-primary !py-2 !px-4 text-sm">Get Started</Link>
        </div>
      </nav>

      <header className="max-w-5xl mx-auto text-center px-6 pt-16 pb-20">
        <motion.span initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="pill mb-5 inline-flex">
          <Sparkles size={14} className="mr-1" /> Final Year AIML Major Project
        </motion.span>
        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-tight"
        >
          Understand any research paper
          <span className="block bg-gradient-to-r from-brand-600 to-purple-600 bg-clip-text text-transparent">in minutes, not hours.</span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mt-6 text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto"
        >
          PaperPilot AI reads, summarizes, and explains academic papers using free, open-source
          AI models running entirely on your own machine — no subscriptions, no API keys.
        </motion.p>
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="mt-8 flex items-center justify-center gap-4">
          <Link to="/register" className="btn-primary text-base">
            Start Analyzing Papers <ArrowRight size={16} />
          </Link>
          <Link to="/login" className="btn-secondary text-base">I already have an account</Link>
        </motion.div>
      </header>

      <section className="max-w-6xl mx-auto px-6 pb-24">
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="glass-card p-6 hover:shadow-glow transition"
            >
              <div className="h-11 w-11 rounded-xl bg-brand-100 dark:bg-brand-900/40 flex items-center justify-center text-brand-600 dark:text-brand-300 mb-4">
                <f.icon size={22} />
              </div>
              <h3 className="font-bold text-slate-800 dark:text-white mb-1.5">{f.title}</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <footer className="border-t border-slate-200 dark:border-slate-800 py-8 text-center text-sm text-slate-500">
        Built with FastAPI, React & open-source Hugging Face models — PaperPilot AI © {new Date().getFullYear()}
      </footer>
    </div>
  )
}
