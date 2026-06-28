import { useState, useEffect } from 'react'
import { PlusIcon, TrashIcon, SparklesIcon, CheckIcon } from '@heroicons/react/24/outline'
import { shoppingApi } from '../api/shopping.js'
import toast from 'react-hot-toast'

const PRIORITY_COLORS = { 1: 'bg-gray-100 text-gray-600', 2: 'bg-yellow-100 text-yellow-700', 3: 'bg-red-100 text-red-700' }
const PRIORITY_LABELS = { 1: 'Low', 2: 'Medium', 3: 'High' }

export default function ShoppingList() {
  const [lists, setLists] = useState([])
  const [activeList, setActiveList] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [newItem, setNewItem] = useState({ name: '', quantity: 1, unit: 'units', priority: 1 })
  const [adding, setAdding] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const data = await shoppingApi.getLists()
      setLists(data)
      setActiveList(data.find(l => l.is_active) || data[0] || null)
    } catch {
      toast.error('Failed to load shopping lists')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleAutoGenerate = async () => {
    setGenerating(true)
    try {
      const added = await shoppingApi.autoGenerate()
      toast.success(`Added ${added.length} items from inventory analysis`)
      await load()
    } catch {
      toast.error('Failed to auto-generate')
    } finally {
      setGenerating(false)
    }
  }

  const handleAddItem = async (e) => {
    e.preventDefault()
    if (!activeList) return
    setAdding(true)
    try {
      await shoppingApi.addItem(activeList.id, { ...newItem, quantity: Number(newItem.quantity) })
      setNewItem({ name: '', quantity: 1, unit: 'units', priority: 1 })
      await load()
      toast.success('Item added')
    } catch {
      toast.error('Failed to add item')
    } finally {
      setAdding(false)
    }
  }

  const handleToggle = async (item) => {
    const newStatus = item.status === 'pending' ? 'purchased' : 'pending'
    try {
      await shoppingApi.updateItem(item.id, { status: newStatus })
      await load()
    } catch {
      toast.error('Failed to update item')
    }
  }

  const handleDelete = async (itemId) => {
    try {
      await shoppingApi.deleteItem(itemId)
      await load()
    } catch {
      toast.error('Failed to delete item')
    }
  }

  const items = activeList?.items || []
  const pending = items.filter(i => i.status === 'pending').sort((a, b) => b.priority - a.priority)
  const purchased = items.filter(i => i.status === 'purchased')

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Shopping List</h1>
          <p className="text-sm text-gray-500 mt-1">{pending.length} items to buy</p>
        </div>
        <button onClick={handleAutoGenerate} disabled={generating} className="btn-primary flex items-center gap-2">
          <SparklesIcon className="w-4 h-4" />
          {generating ? 'Generating...' : 'Auto-Generate'}
        </button>
      </div>

      {/* Add item form */}
      <div className="card">
        <h2 className="font-medium text-gray-700 mb-3 text-sm">Add Item</h2>
        <form onSubmit={handleAddItem} className="flex flex-wrap gap-2">
          <input required className="input-field flex-1 min-w-40" placeholder="Item name"
            value={newItem.name} onChange={e => setNewItem(f => ({ ...f, name: e.target.value }))} />
          <input type="number" min="0.01" step="0.01" className="input-field w-20"
            value={newItem.quantity} onChange={e => setNewItem(f => ({ ...f, quantity: e.target.value }))} />
          <select className="input-field w-24" value={newItem.unit}
            onChange={e => setNewItem(f => ({ ...f, unit: e.target.value }))}>
            {['units', 'g', 'kg', 'ml', 'L', 'pack', 'can'].map(u => <option key={u}>{u}</option>)}
          </select>
          <select className="input-field w-28" value={newItem.priority}
            onChange={e => setNewItem(f => ({ ...f, priority: Number(e.target.value) }))}>
            <option value={1}>Low</option>
            <option value={2}>Medium</option>
            <option value={3}>High</option>
          </select>
          <button type="submit" disabled={adding || !activeList} className="btn-primary flex items-center gap-1">
            <PlusIcon className="w-4 h-4" />
            {adding ? '...' : 'Add'}
          </button>
        </form>
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-4 border-primary-600 border-t-transparent" />
        </div>
      ) : (
        <>
          {/* Pending items */}
          {pending.length > 0 && (
            <div className="card">
              <h2 className="font-semibold text-gray-800 mb-3">To Buy ({pending.length})</h2>
              <div className="space-y-2">
                {pending.map(item => (
                  <div key={item.id} className="flex items-center gap-3 py-2 border-b border-gray-50 last:border-0">
                    <button onClick={() => handleToggle(item)}
                      className="w-5 h-5 border-2 border-gray-300 rounded flex items-center justify-center hover:border-primary-500 transition-colors shrink-0">
                    </button>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800">{item.name}</p>
                      {item.reason && <p className="text-xs text-gray-400">{item.reason}</p>}
                    </div>
                    <span className="text-xs text-gray-500 shrink-0">{item.quantity} {item.unit}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium shrink-0 ${PRIORITY_COLORS[item.priority]}`}>
                      {PRIORITY_LABELS[item.priority]}
                    </span>
                    {item.is_auto_generated && (
                      <span className="text-xs bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded shrink-0">auto</span>
                    )}
                    <button onClick={() => handleDelete(item.id)} className="text-gray-300 hover:text-red-500 shrink-0">
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Purchased items */}
          {purchased.length > 0 && (
            <div className="card opacity-70">
              <h2 className="font-semibold text-gray-600 mb-3 flex items-center gap-2">
                <CheckIcon className="w-4 h-4" />
                Purchased ({purchased.length})
              </h2>
              <div className="space-y-1">
                {purchased.map(item => (
                  <div key={item.id} className="flex items-center gap-3 py-1.5">
                    <button onClick={() => handleToggle(item)}
                      className="w-5 h-5 bg-primary-500 rounded flex items-center justify-center shrink-0">
                      <CheckIcon className="w-3 h-3 text-white" />
                    </button>
                    <span className="text-sm text-gray-400 line-through flex-1">{item.name}</span>
                    <span className="text-xs text-gray-300">{item.quantity} {item.unit}</span>
                    <button onClick={() => handleDelete(item.id)} className="text-gray-200 hover:text-red-400 shrink-0">
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {items.length === 0 && (
            <div className="text-center py-16 text-gray-500">
              <p className="text-4xl mb-4">🛒</p>
              <p>Your shopping list is empty.</p>
              <p className="text-sm mt-1">Use Auto-Generate to add items from your inventory analysis.</p>
            </div>
          )}
        </>
      )}
    </div>
  )
}
