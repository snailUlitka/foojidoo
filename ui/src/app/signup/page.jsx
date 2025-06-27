'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiFetch } from '@/lib/api'

export default function SignUpPage() {
  const router = useRouter()
  const [form, setForm] = useState({
    name: '',
    password: '',
    address: '',
    phone: '',
  })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async e => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await apiFetch('/user/users/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail?.[0]?.msg || res.statusText)
      }
      // On success, redirect to login or home
      router.push('/login')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center pt-20 bg-beige-100">
      <h1 className="text-2xl font-semibold text-brown-700 mb-8">
        Create Account
      </h1>

      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md flex flex-col space-y-4"
      >
        {error && (
          <p className="text-red-500 text-center">{error}</p>
        )}

        {/* Name input */}
        <input
          name="name"
          value={form.name}
          onChange={handleChange}
          placeholder="Name"
          required
          className="bg-beige-50 rounded-full px-4 py-2 text-brown-700 focus:outline-none"
        />

        {/* Password input */}
        <input
          name="password"
          type="password"
          value={form.password}
          onChange={handleChange}
          placeholder="Password"
          required
          className="bg-beige-50 rounded-full px-4 py-2 text-brown-700 focus:outline-none"
        />

        {/* Address input */}
        <input
          name="address"
          value={form.address}
          onChange={handleChange}
          placeholder="Address"
          required
          className="bg-beige-50 rounded-full px-4 py-2 text-brown-700 focus:outline-none"
        />

        {/* Phone input */}
        <input
          name="phone"
          value={form.phone}
          onChange={handleChange}
          placeholder="Phone"
          required
          className="bg-beige-50 rounded-full px-4 py-2 text-brown-700 focus:outline-none"
        />

        {/* Submit button */}
        <button
          type="submit"
          disabled={loading}
          className="bg-beige-200 rounded-full px-6 py-2 font-semibold text-brown-700 hover:bg-beige-300 disabled:opacity-50"
        >
          {loading ? 'Creating…' : 'Create Account'}
        </button>
      </form>
    </div>
  )
}
