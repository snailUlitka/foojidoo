'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiFetch } from '@/lib/api'

export default function LoginPage() {
  const router = useRouter()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = e => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async e => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    // Prepare URL-encoded body
    const body = new URLSearchParams({
      username: form.username,
      password: form.password,
      grant_type: 'password',
    })

    try {
      const res = await apiFetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString(),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail?.[0]?.msg || res.statusText)
      }

      const data = await res.json()
      // Expected: { access_token, token_type, refresh_token, ... }
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)

      // Redirect to home or menu
      router.push('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center pt-20 bg-beige-100">
      <h1 className="text-2xl font-semibold text-brown-700 mb-8">
        Login
      </h1>

      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm flex flex-col space-y-4"
      >
        {error && <p className="text-red-500 text-center">{error}</p>}

        {/* Username */}
        <input
          name="username"
          type="text"
          value={form.username}
          onChange={handleChange}
          placeholder="Username"
          required
          className="bg-beige-50 rounded-full px-4 py-2 text-brown-700 focus:outline-none"
        />

        {/* Password */}
        <input
          name="password"
          type="password"
          value={form.password}
          onChange={handleChange}
          placeholder="Password"
          required
          className="bg-beige-50 rounded-full px-4 py-2 text-brown-700 focus:outline-none"
        />

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="bg-beige-200 rounded-full px-6 py-2 font-semibold text-brown-700 hover:bg-green-300 disabled:opacity-50"
        >
          {loading ? 'Logging in…' : 'Login'}
        </button>
      </form>
    </div>
  )
}
