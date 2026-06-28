import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { PlusIcon, FunnelIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'
import { inventoryApi } from '../api/inventory.js'
import InventoryCard from '../components/InventoryCard.jsx'
import toast from 'react-hot-toast'

const LOCATIONS = ['', 'refrigerator', 'pantry', 'freezer']
const STATUSES = ['', 'fresh', 'expiring_soon', 'expired']

export default function Inventory() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ storage_location: '', expiry_status: '', search: '' })

  const load = async () => {
    setLoading(true)
    try {
      const params = {}
      if (filters.storage_location) params.storage_location = filters.storage_location
      if (filters.expiry_status) params.expiry_status = filters.expiry_status
      if (filters.search) params.search = filters.search
      setItems(await inventoryApi.list(params))
    } catch {
      toast.error('Failed to load inventory')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [filters])

  const handleDelete = async (id) => {
    if (!confirm('Delete this item?')) return
    try {
      await inventoryApi.delete(id)
      setItems(prev => prev.filter(i => i.id !== id))
      toast.success('Item deleted')
    } catch {
      toast.error('Failed to delete item')
    }
  }

  const handleConsume = async (item) => {
    const qty = prompt(`How much ${item.unit} of ${item.name} did you use?`, '1')
    if (!qty || isNaN(qty) || Number(qty) <= 0) return
    try {
      const updated = await inventoryApi.consume(item.id, Number(qty))
      setItems(prev => prev.map(i => i.id === item.id ? updated : i))
      toast.success(`Consumed ${qty} ${item.unit} of ${item.name}`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to record consumption')
    }
  }

  const grouped = {
    refrigerator: items.filter(i => i.storage_location === 'refrigerator'),
    pantry: items.filter(i => i.storage_location === 'pantry'),
    freezer: items.filter(i => i.storage_location === 'freezer'),
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inventory</h1>
          <p className="text-sm text-gray-500 mt-1">{items.length} items tracked</p>
        </div>
        <Link to="/inventory/add" className="btn-primary flex items-center gap-2 self-start sm:self-auto">
          <PlusIcon className="w-4 h-4" />
          Add Item
        </Link>
      </div>

      {/* Filters */}
      <div className="card py-4">
        <div className="flex flex-wrap gap-3 items-center">
          <FunnelIcon className="w-4 h-4 text-gray-400" />
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-2.5 top-2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search items..."
              className="input-field pl-8 py-1.5 text-sm w-48"
              value={filters.search}
              onChange={e => setFilters(f => ({ ...f, search: e.target.value }))}
            />
          </div>
          <select
            className="input-field py-1.5 text-sm w-auto"
            value={filters.storage_location}
            onChange={e => setFilters(f => ({ ...f, storage_location: e.target.value }))}
          >
            <option value="">All Locations</option>
            <option value="refrigerator">🧊 Refrigerator</option>
            <option value="pantry">🏠 Pantry</option>
            <option value="freezer">❄️ Freezer</option>
          </select>
          <select
            className="input-field py-1.5 text-sm w-auto"
            value={filters.expiry_status}
            onChange={e => setFilters(f => ({ ...f, expiry_status: e.target.value }))}
          >
            <option value="">All Status</option>
            <option value="fresh">✅ Fresh</option>
            <option value="expiring_soon">⚠️ Expiring Soon</option>
            <option value="expired">🗑️ Expired</option>
          </select>
          {(filters.storage_location || filters.expiry_status || filters.search) && (
            <button
              onClick={() => setFilters({ storage_location: '', expiry_status: '', search: '' })}
              className="text-xs text-gray-500 hover:text-gray-800 underline"
            >
              Clear filters
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-4 border-primary-600 border-t-transparent" />
        </div>
      ) : items.length === 0 ? (
        <div className="text-center py-16">
          <p className="text-4xl mb-4">📦</p>
          <p className="text-gray-500">No items found. Add your first item!</p>
          <Link to="/inventory/add" className="btn-primary mt-4 inline-block">Add Item</Link>
        </div>
      ) : filters.storage_location ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {items.map(item => (
            <InventoryCard key={item.id} item={item} onDelete={handleDelete} onConsume={handleConsume} />
          ))}
        </div>
      ) : (
        Object.entries(grouped).map(([loc, locItems]) => locItems.length > 0 && (
          <section key={loc}>
            <h2 className="text-base font-semibold text-gray-700 mb-3 flex items-center gap-2">
              {loc === 'refrigerator' ? '🧊' : loc === 'pantry' ? '🏠' : '❄️'}
              {loc.charAt(0).toUpperCase() + loc.slice(1)}
              <span className="text-xs font-normal text-gray-400">({locItems.length})</span>
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {locItems.map(item => (
                <InventoryCard key={item.id} item={item} onDelete={handleDelete} onConsume={handleConsume} />
              ))}
            </div>
          </section>
        ))
      )}
    </div>
  )
}
