import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext.jsx'
import Sidebar from './components/Sidebar.jsx'
import Navbar from './components/Navbar.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Inventory from './pages/Inventory.jsx'
import AddItem from './pages/AddItem.jsx'
import ReceiptUpload from './pages/ReceiptUpload.jsx'
import BarcodeScanner from './pages/BarcodeScanner.jsx'
import Recipes from './pages/Recipes.jsx'
import ShoppingList from './pages/ShoppingList.jsx'
import Analytics from './pages/Analytics.jsx'
import Profile from './pages/Profile.jsx'

function ProtectedLayout({ children }) {
  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-600 border-t-transparent" />
      </div>
    )
  }
  if (!user) return <Navigate to="/login" replace />
  return <ProtectedLayout>{children}</ProtectedLayout>
}

export default function App() {
  const { user } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/dashboard" replace /> : <Register />} />

      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/inventory" element={<ProtectedRoute><Inventory /></ProtectedRoute>} />
      <Route path="/inventory/add" element={<ProtectedRoute><AddItem /></ProtectedRoute>} />
      <Route path="/receipt" element={<ProtectedRoute><ReceiptUpload /></ProtectedRoute>} />
      <Route path="/barcode" element={<ProtectedRoute><BarcodeScanner /></ProtectedRoute>} />
      <Route path="/recipes" element={<ProtectedRoute><Recipes /></ProtectedRoute>} />
      <Route path="/shopping" element={<ProtectedRoute><ShoppingList /></ProtectedRoute>} />
      <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
