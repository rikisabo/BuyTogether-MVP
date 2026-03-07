import { Routes, Route, Link } from 'react-router-dom'
import { Home } from './pages/Home'
import { DealDetails } from './pages/DealDetails'
import { Admin } from './pages/Admin'
import { Toast } from './components/Toast'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="container mx-auto px-4 py-4 flex gap-6">
          <Link to="/" className="font-bold text-lg hover:text-blue-500">
            buyTogether
          </Link>
          <Link to="/" className="hover:text-blue-500">
            Home
          </Link>
          <Link to="/admin" className="hover:text-blue-500">
            Admin
          </Link>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/deals/:dealId" element={<DealDetails />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>

      <Toast />
    </div>
  )
}
