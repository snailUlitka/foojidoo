import Link from 'next/link'
import { ShoppingCart, User } from 'lucide-react'

export default function Navbar() {
  return (
    <header className="bg-beige-200 p-4 flex items-center justify-between">
      {/* Logo + brand name */}
      <Link href="/" className="flex items-center space-x-2">
        <img src="/logo.svg" alt="foojidoo logo" className="h-8 w-8" />
        <span className="text-xl font-semibold text-brown-700">foojidoo</span>
      </Link>

      {/* Cart and profile icons */}
      <nav className="flex items-center space-x-4 text-brown-700">
        <Link href="/cart" aria-label="Cart">
          <ShoppingCart size={24} />
        </Link>
        <Link href="/account" aria-label="Account">
          <User size={24} />
        </Link>
      </nav>
    </header>
  )
}
