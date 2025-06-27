// Base URL from env
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL

/**
 * Fetch wrapper that prefixes your base URL, injects the Bearer token,
 * and redirects to /login on 401.
 *
 * @param {string} path    — API path (e.g. '/user/users/me')
 * @param {RequestInit} options
 */
export async function apiFetch(path, options = {}) {
  // Full URL
  const url = `${API_BASE}${path}`

  // Merge headers
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  // Inject token client‑side
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  // Perform request
  const res = await fetch(url, {
    ...options,
    headers,
  })

  // If unauthorized, redirect to login
  if (res.status === 401 && typeof window !== 'undefined') {
    // Optionally clear any stored tokens
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    // Redirect
    window.location.href = '/login'
    // Return a never‑resolving promise so calling code doesn’t continue
    return new Promise(() => {})
  }

  return res
}
