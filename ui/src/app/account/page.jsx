'use client'

import { useState, useEffect } from 'react'
import { apiFetch } from '@/lib/api'
import { useNotification } from '@/components/NotificationProvider'

export default function AccountPage() {
  // user profile state
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // modal state
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [fieldToEdit, setFieldToEdit] = useState(null)
  const [inputValue, setInputValue] = useState('')

  // notify
  const { notify } = useNotification()

  useEffect(() => {
    async function loadProfile() {
      try {
        const res = await apiFetch('/user/users/me')
        if (!res.ok) throw new Error(res.statusText)
        const data = await res.json()
        setProfile(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    loadProfile()
  }, [])

  // open modal for a given field
  const openEditor = field => {
    setFieldToEdit(field)
    setInputValue(profile[field] || '')
    setIsModalOpen(true)
  }

  // save updated field
  const saveField = async () => {
    try {
      const updated = { ...profile, [fieldToEdit]: inputValue }
      // password field must be non-empty; if user isn't changing it, keep current or force change
      const body = {
        name: updated.name,
        password: updated.password === undefined ? null : updated.password,
        address: updated.address,
        phone: updated.phone,
      }
      const res = await apiFetch('/user/users/me', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail?.[0]?.msg || res.statusText)
      }
      const newProfile = await res.json()
      setProfile(newProfile)
      setIsModalOpen(false)
      setFieldToEdit(null)
    } catch (err) {
      notify('Error updating profile: ' + err.message)
    }
  }

  if (loading) return <p className="p-4 text-brown-700">Loading...</p>
  if (error)   return <p className="p-4 text-red-500">Error: {error}</p>

  return (
    <div className="p-6 bg-beige-100 min-h-screen">
      <h1 className="text-2xl font-semibold text-brown-700 mb-6">My Account</h1>

      <div className="space-y-4 max-w-md">
        {['name','address','phone'].map(field => (
          <div key={field} className="flex justify-between items-center bg-white p-4 rounded-lg shadow">
            <span className="text-brown-700 capitalize">{field}:</span>
            <div className="flex items-center space-x-2">
              <span className="text-brown-900">{profile[field]}</span>
              <button
                onClick={() => openEditor(field)}
                className="text-sm text-beige-200 bg-brown-700 px-3 py-1 rounded-full hover:bg-gray-300"
              >
                Edit
              </button>
            </div>
          </div>
        ))}

        {/* Password field (masked) */}
        <div className="flex justify-between items-center bg-white p-4 rounded-lg shadow">
          <span className="text-brown-700 capitalize">password:</span>
          <button
            onClick={() => openEditor('password')}
            className="text-sm text-beige-200 bg-brown-700 px-3 py-1 rounded-full hover:bg-gray-300"
          >
            Change
          </button>
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg w-full max-w-sm p-6 shadow-lg">
            <h2 className="text-xl font-semibold text-brown-700 mb-4">
              Edit {fieldToEdit}
            </h2>
            <input
              type={fieldToEdit === 'password' ? 'password' : 'text'}
              className="w-full bg-beige-50 rounded-full px-4 py-2 text-brown-700 focus:outline-none mb-4"
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 rounded-full bg-brown-700 text-gray-700 hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={saveField}
                className="px-4 py-2 rounded-full bg-brown-700 text-beige-200 hover:bg-gray-300"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
