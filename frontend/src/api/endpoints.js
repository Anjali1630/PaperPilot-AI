import client from './client'

// ---------- Auth ----------
export const registerUser = (data) => client.post('/auth/register', data)
export const loginUser = (data) => client.post('/auth/login', data)
export const getMe = () => client.get('/auth/me')
export const updateSettings = (data) => client.put('/auth/settings', data)

// ---------- Papers ----------
export const uploadPapers = (files, onUploadProgress) => {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))
  return client.post('/papers/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress,
  })
}
export const listPapers = (search = '') => client.get('/papers', { params: { search } })
export const getPaper = (id) => client.get(`/papers/${id}`)
export const deletePaper = (id) => client.delete(`/papers/${id}`)
export const reanalyzePaper = (id) => client.post(`/papers/${id}/reanalyze`)

// ---------- Chat ----------
export const getChatHistory = (paperId) => client.get(`/papers/${paperId}/chat`)
export const askQuestion = (paperId, question) => client.post(`/papers/${paperId}/chat`, { question })

// ---------- Compare ----------
export const comparePapers = (paperIds) => client.post('/compare', { paper_ids: paperIds })

// ---------- Dashboard ----------
export const getDashboard = () => client.get('/dashboard')

// ---------- Export ----------
export const exportUrl = (paperId, fmt) => `/api/papers/${paperId}/export/${fmt}`
