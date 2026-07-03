import { useState } from 'react'
import { Moon, Sun, Save, User } from 'lucide-react'
import AppLayout from '../components/AppLayout'
import { Section } from '../components/UI'
import { useAuth } from '../context/AuthContext'
import { updateSettings } from '../api/endpoints'

export default function SettingsPage() {
  const { user, updateUserLocal } = useAuth()
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [darkMode, setDarkMode] = useState(user?.dark_mode || false)
  const [summaryPref, setSummaryPref] = useState(user?.summary_length_pref || 'standard')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const toggleDark = (val) => {
    setDarkMode(val)
    document.documentElement.classList.toggle('dark', val)
  }

  const handleSave = async () => {
    setSaving(true)
    setSaved(false)
    try {
      const res = await updateSettings({ full_name: fullName, dark_mode: darkMode, summary_length_pref: summaryPref })
      updateUserLocal(res.data)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  return (
    <AppLayout title="Settings">
      <div className="mb-6">
        <h1 className="text-2xl font-extrabold text-slate-800 dark:text-white">Settings</h1>
        <p className="text-sm text-slate-500">Manage your account and application preferences.</p>
      </div>

      <div className="max-w-2xl space-y-6">
        <Section title="Account" icon={User}>
          <div className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-slate-500 uppercase">Username</label>
              <input disabled value={user?.username || ''} className="input-field mt-1 opacity-60" />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-500 uppercase">Email</label>
              <input disabled value={user?.email || ''} className="input-field mt-1 opacity-60" />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-500 uppercase">Full Name</label>
              <input value={fullName} onChange={(e) => setFullName(e.target.value)} className="input-field mt-1" placeholder="Your full name" />
            </div>
          </div>
        </Section>

        <Section title="Appearance">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {darkMode ? <Moon size={18} className="text-brand-500" /> : <Sun size={18} className="text-amber-500" />}
              <span className="text-sm font-medium text-slate-700 dark:text-slate-200">Dark Mode</span>
            </div>
            <button
              onClick={() => toggleDark(!darkMode)}
              className={`w-12 h-7 rounded-full transition relative ${darkMode ? 'bg-brand-600' : 'bg-slate-300'}`}
            >
              <span className={`absolute top-1 h-5 w-5 rounded-full bg-white transition-transform ${darkMode ? 'translate-x-6' : 'translate-x-1'}`} />
            </button>
          </div>
        </Section>

        <Section title="Summary Preferences">
          <label className="text-xs font-semibold text-slate-500 uppercase">Default Summary Length</label>
          <select value={summaryPref} onChange={(e) => setSummaryPref(e.target.value)} className="input-field mt-1">
            <option value="short">Executive (Short, ~100 words)</option>
            <option value="standard">Standard (~300 words)</option>
            <option value="detailed">Detailed (~700 words)</option>
          </select>
        </Section>

        <div className="flex items-center gap-3">
          <button onClick={handleSave} disabled={saving} className="btn-primary">
            <Save size={16} /> {saving ? 'Saving...' : 'Save Changes'}
          </button>
          {saved && <span className="text-sm text-emerald-600 font-medium">Saved!</span>}
        </div>
      </div>
    </AppLayout>
  )
}
