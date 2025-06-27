import './globals.css'
import Navbar from '@/components/Navbar'
import { NotificationProvider } from '@/components/NotificationProvider'

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
       <NotificationProvider>
         <Navbar />
         <main className="min-h-screen bg-beige-100">
           {children}
         </main>
       </NotificationProvider>
      </body>
    </html>
  )
}
