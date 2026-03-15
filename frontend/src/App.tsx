import { Routes, Route, Link } from 'react-router-dom'
import { Home } from './pages/Home'
import { DealDetails } from './pages/DealDetails'
import { Admin } from './pages/Admin'
import { Confirm } from './pages/Confirm'
import { Toast } from './components/Toast'

export default function App() {
  return (
    <div dir="rtl" className="min-h-screen bg-slate-50 text-right font-sans">
      <nav className="bg-white shadow">
        <div className="container mx-auto px-4 py-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Link to="/" className="text-2xl font-extrabold text-indigo-600 hover:text-indigo-500">
            BuyTogether🥕🥕
            </Link>
            <span className="text-sm text-gray-500">מקום הישראלי לחיסכון בקנייה יחד</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/" className="text-sm text-slate-700 hover:text-indigo-600">בית</Link>
            <Link to="/admin" className="text-sm text-slate-700 hover:text-indigo-600">ניהול</Link>
          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/deals/:dealId" element={<DealDetails />} />
        <Route path="/confirm/:token" element={<Confirm />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>

      <Toast />
    </div>
  )
}
