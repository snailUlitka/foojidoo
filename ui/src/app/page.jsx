'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { apiFetch } from '@/lib/api'

export default function HomePage() {
  const [restaurants, setRestaurants] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const res = await apiFetch('/restaurant/restaurants/')
        if (!res.ok) throw new Error(res.statusText)
        const data = await res.json()
        setRestaurants(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-beige-100">
        <p className="text-brown-700">Loading restaurants…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-beige-100">
        <p className="text-red-500">Error: {error}</p>
      </div>
    )
  }

  return (
    <div className="p-4 bg-beige-100 min-h-screen">
      <h1 className="text-2xl font-semibold text-brown-700 mb-6">
        Choose a Restaurant
      </h1>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {restaurants.map(r => (
          <Link
            key={r.restaurant_id}
            href={`/restaurant/${r.restaurant_id}/menu`}
            className="block bg-white rounded-lg p-4 shadow hover:shadow-md transition"
          >
            <button className="w-full text-left text-brown-700 font-medium">
              {r.name}
            </button>
          </Link>
        ))}
      </div>
    </div>
  )
}
