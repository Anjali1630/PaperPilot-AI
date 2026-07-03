import { useEffect, useRef, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Send, MessageSquare, Sparkles } from 'lucide-react'
import AppLayout from '../components/AppLayout'
import { Loader } from '../components/UI'
import { getPaper, getChatHistory, askQuestion } from '../api/endpoints'

const SUGGESTED = [
  'What dataset was used?',
  'What accuracy was achieved?',
  'What is the proposed algorithm?',
  'Summarize the conclusion.',
]

export default function Chat() {
  const { id } = useParams()
  const [paper, setPaper] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [loading, setLoading] = useState(true)
  const bottomRef = useRef(null)

  useEffect(() => {
    Promise.all([getPaper(id), getChatHistory(id)])
      .then(([p, h]) => {
        setPaper(p.data)
        setMessages(h.data)
      })
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text) => {
    const question = (text ?? input).trim()
    if (!question || sending) return
    setInput('')
    setSending(true)
    setMessages((prev) => [...prev, { id: `tmp-${Date.now()}`, role: 'user', content: question, created_at: new Date().toISOString() }])
    try {
      const res = await askQuestion(id, question)
      setMessages((prev) => [...prev, res.data])
    } catch (err) {
      setMessages((prev) => [...prev, { id: `err-${Date.now()}`, role: 'assistant', content: 'Something went wrong answering that. Please try again.', created_at: new Date().toISOString() }])
    } finally {
      setSending(false)
    }
  }

  if (loading) return <AppLayout title="Chat"><Loader label="Loading paper..." /></AppLayout>

  return (
    <AppLayout title="Chat with PDF">
      <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-140px)]">
        <div className="flex items-center gap-3 mb-4">
          <Link to={`/papers/${id}`} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"><ArrowLeft size={18} /></Link>
          <div className="min-w-0">
            <h1 className="font-bold text-slate-800 dark:text-white truncate">{paper?.title || paper?.filename}</h1>
            <p className="text-xs text-slate-500">Ask anything — answers are grounded only in this paper.</p>
          </div>
        </div>

        <div className="glass-card flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-10">
              <MessageSquare size={32} className="mx-auto text-brand-300 mb-3" />
              <p className="text-sm text-slate-500 mb-4">Try asking one of these:</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {SUGGESTED.map((s) => (
                  <button key={s} onClick={() => send(s)} className="pill hover:bg-brand-100 dark:hover:bg-brand-800 transition">{s}</button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m) => (
            <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-line ${
                m.role === 'user'
                  ? 'bg-brand-600 text-white rounded-br-sm'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200 rounded-bl-sm'
              }`}>
                {m.content}
              </div>
            </div>
          ))}

          {sending && (
            <div className="flex justify-start">
              <div className="bg-slate-100 dark:bg-slate-800 rounded-2xl rounded-bl-sm px-4 py-2.5 flex items-center gap-1.5">
                <Sparkles size={14} className="text-brand-500 animate-pulse" />
                <span className="text-xs text-slate-500">Thinking...</span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="mt-4 flex items-center gap-2">
          <input
            className="input-field"
            placeholder="Ask a question about this paper..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
          />
          <button onClick={() => send()} disabled={sending || !input.trim()} className="btn-primary !px-4">
            <Send size={16} />
          </button>
        </div>
      </div>
    </AppLayout>
  )
}
