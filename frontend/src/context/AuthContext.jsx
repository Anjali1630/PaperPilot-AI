import { createContext, useContext, useEffect, useState } from 'react'
import { loginUser, registerUser, getMe } from '../api/endpoints'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('paperpilot_user')
    return stored ? JSON.parse(stored) : null
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('paperpilot_token')
    if (!token) {
      setLoading(false)
      return
    }
    getMe()
      .then((res) => {
        setUser(res.data)
        localStorage.setItem('paperpilot_user', JSON.stringify(res.data))
      })
      .catch(() => {
        localStorage.removeItem('paperpilot_token')
        localStorage.removeItem('paperpilot_user')
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const persist = (data) => {
    localStorage.setItem('paperpilot_token', data.access_token)
    localStorage.setItem('paperpilot_user', JSON.stringify(data.user))
    setUser(data.user)
  }

  const login = async (username, password) => {
    const res = await loginUser({ username, password })
    persist(res.data)
    return res.data.user
  }

  const register = async (payload) => {
    const res = await registerUser(payload)
    persist(res.data)
    return res.data.user
  }

  const logout = () => {
    localStorage.removeItem('paperpilot_token')
    localStorage.removeItem('paperpilot_user')
    setUser(null)
  }

  const updateUserLocal = (partial) => {
    setUser((prev) => {
      const next = { ...prev, ...partial }
      localStorage.setItem('paperpilot_user', JSON.stringify(next))
      return next
    })
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateUserLocal }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
