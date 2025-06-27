'use client'

import { createContext, useContext, useState, useCallback } from 'react'
import { XMarkIcon } from '@heroicons/react/24/outline'

// Toast shape: { id, message, type }
const NotificationContext = createContext()

export function NotificationProvider({ children }) {
  const [toasts, setToasts] = useState([])

  // add a toast
  const notify = useCallback((message, type = 'info') => {
    const id = Date.now().toString()
    setToasts((prev) => [...prev, { id, message, type }])
    // auto-remove after 3s
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 3000)
  }, [])

  // remove manually
  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  return (
    <NotificationContext.Provider value={{ notify, dismiss }}>
      {children}

      {/* Toast container */}
      <div className="fixed bottom-4 right-4 flex flex-col space-y-2 z-50">
        {toasts.map(({ id, message, type }) => (
          <div
            key={id}
            className={`
              max-w-xs px-4 py-2 rounded-lg shadow-lg flex items-center justify-between
              ${type === 'success' ? 'bg-green-100 text-green-800' : ''}
              ${type === 'error'   ? 'bg-red-100 text-red-800'   : ''}
              ${type === 'info'    ? 'bg-blue-100 text-blue-800'  : ''}
            `}
          >
            <span className="flex-1">{message}</span>
            <button onClick={() => dismiss(id)} className="ml-2">
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  )
}

// Hook to use in any component
export function useNotification() {
  const ctx = useContext(NotificationContext)
  if (!ctx) throw new Error('useNotification must be inside NotificationProvider')
  return ctx
}
