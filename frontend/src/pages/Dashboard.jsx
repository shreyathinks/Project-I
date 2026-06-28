import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  ArchiveBoxIcon, ExclamationTriangleIcon, CheckCircleIcon, XCircleIcon,
  PlusIcon, ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { dashboardApi } from '../api/recipes.js'

function StatCard({ icon: Icon, label, value, color, subtext }) {
  return (
    <div className="card">
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-xl ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {subtext && <p className="text-xs text-gray-400 mt-0.5">{subtext}</p>}
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dashboardApi.getSummary()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-primary-600 border-t-transparent" />
      </div>
    )
  }

  if (!data) return <p className="text-gray-500">Failed to load dashboard data.</p>

  const { inventory, expiring_detail, consumption, waste, financials } = data

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Your kitchen at a glance</p>
        </div>
        <Link to="/inventory/add" className="btn-primary flex items-center gap-2">
          <PlusIcon className="w-4 h-4" />
          Add Item
        </Link>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={ArchiveBoxIcon} label="Total Items" value={inventory.total}
          color="bg-primary-600" subtext={`${inventory.fresh} fresh`} />
        <StatCard icon={ExclamationTriangleIcon} label="Expiring Soon" value={inventory.expiring_soon}
          color="bg-yellow-500" subtext="within 3 days" />
        <StatCard icon={XCircleIcon} label="Expired" value={inventory.expired}
          color="bg-red-500" subtext="action needed" />
        <StatCard icon={CheckCircleIcon} label="Money Saved" value={`$${financials.estimated_money_saved}`}
          color="bg-blue-500" subtext="from consumed items" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Storage breakdown */}
        <div className="card">
          <h2 className="font-semibold text-gray-800 mb-4">By Location</h2>
          <div className="space-y-3">
            {[
              { label: '🧊 Refrigerator', key: 'refrigerator', color: 'bg-blue-500' },
              { label: '🏠 Pantry', key: 'pantry', color: 'bg-amber-500' },
              { label: '❄️ Freezer', key: 'freezer', color: 'bg-cyan-500' },
            ].map(({ label, key, color }) => {
              const count = inventory.by_location[key] || 0
              const pct = inventory.total > 0 ? Math.round((count / inventory.total) * 100) : 0
              return (
                <div key={key}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">{label}</span>
                    <span className="font-medium text-gray-800">{count}</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Expiring items */}
        <div className="card lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-800">Expiring Soon</h2>
            <Link to="/inventory?expiry=expiring_soon" className="text-xs text-primary-600 hover:underline">
              View all
            </Link>
          </div>
          {expiring_detail.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-6">✅ Nothing expiring in the next 3 days!</p>
          ) : (
            <div className="space-y-2">
              {expiring_detail.map(item => (
                <div key={item.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                  <div>
                    <p className="text-sm font-medium text-gray-800">{item.name}</p>
                    <p className="text-xs text-gray-400">{item.quantity} {item.unit} · {item.storage_location}</p>
                  </div>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                    item.days_until_expiry === 0 ? 'bg-red-100 text-red-700' :
                    item.days_until_expiry <= 1 ? 'bg-orange-100 text-orange-700' :
                    'bg-yellow-100 text-yellow-700'
                  }`}>
                    {item.days_until_expiry === 0 ? 'Today' : `${item.days_until_expiry}d`}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Weekly consumption chart */}
      <div className="card">
        <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <ArrowTrendingUpIcon className="w-5 h-5 text-primary-600" />
          Weekly Consumption (last 8 weeks)
        </h2>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={consumption.weekly_trend} margin={{ top: 0, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="week" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="consumed" fill="#16a34a" radius={[4, 4, 0, 0]} name="Items consumed" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { to: '/receipt', label: 'Scan Receipt', icon: '📄' },
          { to: '/barcode', label: 'Scan Barcode', icon: '📲' },
          { to: '/recipes', label: 'Find Recipes', icon: '📖' },
          { to: '/shopping', label: 'Shopping List', icon: '🛒' },
        ].map(({ to, label, icon }) => (
          <Link key={to} to={to} className="card text-center hover:shadow-md transition-shadow hover:border-primary-200 border-2 border-transparent cursor-pointer">
            <div className="text-3xl mb-2">{icon}</div>
            <p className="text-sm font-medium text-gray-700">{label}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
