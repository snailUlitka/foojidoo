'use client'

import { useState, useEffect } from 'react'
import { apiFetch } from '@/lib/api'
import { TrashIcon } from '@heroicons/react/24/outline'
import { useNotification } from '@/components/NotificationProvider'

export default function CartPage() {
  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [paymentMethod, setPaymentMethod] = useState('cash')
  const { notify } = useNotification()

  useEffect(() => {
    async function loadOrder() {
      try {
        const res = await apiFetch('/order/orders/')
        if (!res.ok) throw new Error(res.statusText)
        const data = await res.json()
        setOrder(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    loadOrder()
  }, [])

  const removeItem = async (restaurantId, dishId) => {
    try {
      const res = await apiFetch(`/order/orders/items/${restaurantId}/${dishId}`, {
        method: 'DELETE',
      })
      if (!res.ok) throw new Error('Failed to remove item')

      // Reload order after removing
      const updated = await apiFetch('/order/orders/')
      const data = await updated.json()
      setOrder(data)
    } catch (err) {
      notify(err.message)
    }
  }

  const confirmOrder = async () => {
    // TODO: add confirm order functionality
    notify('Order confirmed!')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-beige-100">
        <p className="text-brown-700">Loading your cart…</p>
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

  if (!order || order.items.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-beige-100">
        <p className="text-brown-700">Your cart is empty.</p>
      </div>
    )
  }

  return (
    <div className="p-6 bg-beige-100 min-h-screen flex flex-col">
      <h1 className="text-2xl font-semibold text-brown-700 mb-6">Your Cart</h1>

      <div className="space-y-4 flex-1">
        {order.items.map(item => (
          <div
            key={`${item.restaurant_id}-${item.dish_id}`}
            className="bg-white p-4 rounded-lg shadow flex justify-between items-center"
          >
            <div>
              <h2 className="text-brown-800 font-medium">{item.name}</h2>
              <p className="text-brown-600 text-sm">Quantity: {item.quantity}</p>
            </div>
            <button
              onClick={() => removeItem(item.restaurant_id, item.dish_id)}
              className="text-brown-700 hover:text-red-600"
            >
              <TrashIcon className="h-6 w-6" />
            </button>
          </div>
        ))}
      </div>

      <div className="mt-8">
        <label className="block mb-2 text-brown-700 font-medium">
          Select Payment Method
        </label>
        <select
          value={paymentMethod}
          onChange={e => setPaymentMethod(e.target.value)}
          className="w-full bg-white border border-gray-300 rounded-full px-4 py-2 text-brown-700 focus:outline-none mb-6"
        >
          <option value="cash">Cash</option>
          <option value="card_online">Card Online</option>
          <option value="card_courier">Card to Courier</option>
        </select>

        <div className="w-full bg-brown-700 text-beige-200 rounded-full px-6 py-3 font-semibold flex justify-center items-center">
            <button
              onClick={confirmOrder}
              className="bg-brown-700 text-beige-200 rounded-full px-6 py-3 font-semibold hover:bg-green-300"
            >
              Confirm Order
            </button>
        </div>
      </div>
    </div>
  )
}
