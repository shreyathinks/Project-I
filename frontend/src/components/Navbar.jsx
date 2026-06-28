import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { BellIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline'
import { useAuth } from '../context/AuthContext.jsx'
import { dashboardApi } from '../api/recipes.js'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [unread, setUnread] = useState(0)
  const [showNotifications, setShowNotifications] = useState(false)
  const [notifications, setNotifications] = useState([])

  useEffect(() => {
    dashboardApi.getSummary()
      .then(data => setUnread(data.notifications.unread_count))
      .catch(() => {})
  }, [])

  const handleBellClick = async () => {
    if (!showNotifications) {
      const data = await dashboardApi.getNotifications()
      setNotifications(data)
    }
    setShowNotifications(v => !v)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shrink-0">
      <div>
        <h1 className="text-lg font-semibold text-gray-900">
          Welcome back, {user?.full_name || user?.username} 👋
        </h1>
        <p className="text-xs text-gray-500">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
        </p>
      </div>

      <div className="flex items-center gap-4">
        {/* Notifications bell */}
        <div className="relative">
          <button
            onClick={handleBellClick}
            className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <BellIcon className="w-5 h-5 text-gray-600" />
            {unread > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
                {unread > 9 ? '9+' : unread}
              </span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 top-10 w-80 bg-white border border-gray-200 rounded-xl shadow-lg z-50 max-h-96 overflow-y-auto">
              <div className="p-3 border-b border-gray-100 flex justify-between items-center">
                <span className="font-semibold text-sm text-gray-800">Notifications</span>
                <button
                  onClick={async () => { await dashboardApi.markAllRead(); setUnread(0); setShowNotifications(false) }}
                  className="text-xs text-primary-600 hover:underline"
                >
                  Mark all read
                </button>
              </div>
              {notifications.length === 0 ? (
                <p className="p-4 text-sm text-gray-500 text-center">No notifications</p>
              ) : (
                notifications.slice(0, 10).map(n => (
                  <div
                    key={n.id}
                    className={`p-3 border-b border-gray-50 hover:bg-gray-50 ${!n.is_read ? 'bg-primary-50' : ''}`}
                  >
                    <p className="text-sm font-medium text-gray-800">{n.title}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{n.message}</p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* User avatar */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
            {(user?.username || 'U')[0].toUpperCase()}
          </div>
          <span className="text-sm font-medium text-gray-700 hidden md:block">{user?.username}</span>
        </div>

        <button
          onClick={handleLogout}
          className="p-2 rounded-lg hover:bg-red-50 hover:text-red-600 text-gray-500 transition-colors"
          title="Logout"
        >
          <ArrowRightOnRectangleIcon className="w-5 h-5" />
        </button>
      </div>
    </header>
  )
}
