import { useCallback, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UploadCloud, FileText, X, Loader2 } from 'lucide-react'
import AppLayout from '../components/AppLayout'
import { uploadPapers } from '../api/endpoints'

const MAX_SIZE_MB = 25

export default function Upload() {
  const [files, setFiles] = useState([])
  const [dragging, setDragging] = useState(false)
  const [progress, setProgress] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef(null)
  const navigate = useNavigate()

  const addFiles = (newFiles) => {
    setError('')
    const valid = []
    for (const f of newFiles) {
      if (f.type !== 'application/pdf') {
        setError('Only PDF files are supported.')
        continue
      }
      if (f.size / (1024 * 1024) > MAX_SIZE_MB) {
        setError(`"${f.name}" exceeds the ${MAX_SIZE_MB}MB limit.`)
        continue
      }
      valid.push(f)
    }
    setFiles((prev) => [...prev, ...valid])
  }

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    addFiles(Array.from(e.dataTransfer.files))
  }, [])

  const removeFile = (idx) => setFiles((prev) => prev.filter((_, i) => i !== idx))

  const handleUpload = async () => {
    if (files.length === 0) return
    setUploading(true)
    setError('')
    try {
      const res = await uploadPapers(files, (evt) => {
        setProgress(Math.round((evt.loaded * 100) / evt.total))
      })
      const first = res.data[0]
      navigate(`/papers/${first.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <AppLayout title="Upload">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-extrabold text-slate-800 dark:text-white mb-1">Upload Research Papers</h1>
        <p className="text-sm text-slate-500 mb-6">Drop one or more PDFs — we'll parse, summarize and analyze them automatically.</p>

        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => inputRef.current?.click()}
          className={`glass-card border-2 border-dashed p-12 flex flex-col items-center justify-center text-center cursor-pointer transition ${
            dragging ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-900/20' : 'border-slate-300 dark:border-slate-700'
          }`}
        >
          <UploadCloud size={44} className="text-brand-500 mb-3" />
          <p className="font-semibold text-slate-700 dark:text-slate-200">Drag & drop PDF files here</p>
          <p className="text-sm text-slate-500 mt-1">or click to browse — up to {MAX_SIZE_MB}MB per file</p>
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf"
            multiple
            hidden
            onChange={(e) => addFiles(Array.from(e.target.files))}
          />
        </div>

        {error && <div className="mt-4 rounded-lg bg-red-50 dark:bg-red-950/40 text-red-600 dark:text-red-300 text-sm px-4 py-2.5">{error}</div>}

        {files.length > 0 && (
          <div className="mt-6 space-y-2">
            {files.map((f, i) => (
              <div key={i} className="flex items-center justify-between glass-card px-4 py-3">
                <div className="flex items-center gap-3 min-w-0">
                  <FileText size={18} className="text-brand-600 shrink-0" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-200 truncate">{f.name}</p>
                    <p className="text-xs text-slate-500">{(f.size / (1024 * 1024)).toFixed(2)} MB</p>
                  </div>
                </div>
                <button onClick={() => removeFile(i)} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400">
                  <X size={16} />
                </button>
              </div>
            ))}
          </div>
        )}

        {uploading && (
          <div className="mt-4">
            <div className="h-2 w-full rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
              <div className="h-full bg-brand-600 transition-all" style={{ width: `${progress}%` }} />
            </div>
            <p className="text-xs text-slate-500 mt-1">{progress}% uploaded</p>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={files.length === 0 || uploading}
          className="btn-primary mt-6 w-full sm:w-auto"
        >
          {uploading ? <Loader2 size={16} className="animate-spin" /> : <UploadCloud size={16} />}
          {uploading ? 'Uploading...' : `Analyze ${files.length || ''} Paper${files.length === 1 ? '' : 's'}`}
        </button>
      </div>
    </AppLayout>
  )
}
