'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { apiFetch } from '@/lib/api'
import { EyeIcon, PlusIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { useNotification } from '@/components/NotificationProvider'

export default function MenuPage() {
  const { restaurantId } = useParams()
  const [menu, setMenu] = useState({ restaurant: null, dishes: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedDish, setSelectedDish] = useState(null)

  const { notify } = useNotification()

  useEffect(() => {
    async function loadMenu() {
      try {
        const res = await apiFetch(`/restaurant/restaurants/${restaurantId}/menu`)
        if (!res.ok) throw new Error(res.statusText)
        const data = await res.json()
        setMenu(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    loadMenu()
  }, [restaurantId])

  const openDetails = dish => {
    setSelectedDish(dish)
    setIsModalOpen(true)
  }

  const addToCart = async dish => {
    try {
      const res = await apiFetch('/order/orders/items', {
        method: 'POST',
        body: JSON.stringify({
          restaurant_id: dish.restaurant_id,
          dish_id: dish.dish_id,
          quantity: 1,
        }),
      })
      if (!res.ok) throw new Error('Failed to add to cart')
      // Optionally show a toast here
      notify(`Added “${dish.name}” to cart`)
    } catch (err) {
      notify(err.message)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-beige-100">
        <p className="text-brown-700">Loading menu…</p>
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
        {menu.restaurant?.name} Menu
      </h1>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {menu.dishes.map(dish => (
          <div
            key={dish.dish_id}
            className="bg-white rounded-lg p-4 shadow flex flex-col justify-between"
          >
            <h2 className="text-brown-800 font-medium mb-2">{dish.name}</h2>
            <div className="mt-auto flex items-center justify-between">
              <button
                aria-label="View details"
                onClick={() => openDetails(dish)}
              >
                <EyeIcon className="h-6 w-6 text-brown-700 hover:text-brown-900" />
              </button>
              <button
                aria-label="Add to cart"
                onClick={() => addToCart(dish)}
              >
                <PlusIcon className="h-6 w-6 text-brown-700 hover:text-brown-900" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Details Modal */}
      {isModalOpen && selectedDish && (
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-sm w-full p-6 relative shadow-lg">
            <button
              onClick={() => setIsModalOpen(false)}
              className="absolute top-3 right-3"
              aria-label="Close"
            >
              <XMarkIcon className="h-6 w-6 text-brown-700 hover:text-brown-900" />
            </button>

            <h2 className="text-xl font-semibold text-brown-700 mb-2">
              {selectedDish.name}
            </h2>
            <p className="text-brown-600 mb-4">
              {selectedDish.description || 'No description'}
            </p>
            <button
              onClick={() => {
                addToCart(selectedDish)
                setIsModalOpen(false)
              }}
              className="w-full bg-beige-200 rounded-full px-6 py-2 font-semibold text-brown-700 hover:bg-beige-300"
            >
              Add to Cart
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
