import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { inventoryApi } from '../api/inventory.js'
import toast from 'react-hot-toast'

export default function AddItem() {
  const navigate = useNavigate()
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    name: '', brand: '', quantity: 1, unit: 'units',
    purchase_date: new Date().toISOString().split('T')[0],
    expiry_date: '', storage_location: 'pantry',
    category_id: '', notes: '', price: '',
  })

  useEffect(() => {
    inventoryApi.getCategories().then(setCategories).catch(() => {})
  }, [])

  const set = (key, val) => setForm(f => ({ ...f, [key]: val }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const payload = {
        ...form,
        quantity: Number(form.quantity),
        category_id: form.category_id ? Number(form.category_id) : undefined,
        expiry_date: form.expiry_date || undefined,
        price: form.price ? Number(form.price) : undefined,
      }
      await inventoryApi.create(payload)
      toast.success(`${form.name} added to inventory!`)
      navigate('/inventory')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add item')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Add Inventory Item</h1>
        <p className="text-sm text-gray-500 mt-1">Fill in the details. Expiry date is auto-estimated if left blank.</p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="sm:col-span-2">
            <label className="label">Item Name *</label>
            <input required className="input-field" value={form.name}
              onChange={e => set('name', e.target.value)} placeholder="e.g. Whole Milk" />
          </div>
          <div>
            <label className="label">Brand</label>
            <input className="input-field" value={form.brand}
              onChange={e => set('brand', e.target.value)} placeholder="e.g. Organic Valley" />
          </div>
          <div>
            <label className="label">Category</label>
            <select className="input-field" value={form.category_id}
              onChange={e => set('category_id', e.target.value)}>
              <option value="">Select category...</option>
              {categories.map(c => (
                <option key={c.id} value={c.id}>{c.icon} {c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Quantity *</label>
            <input required type="number" min="0.01" step="0.01" className="input-field"
              value={form.quantity} onChange={e => set('quantity', e.target.value)} />
          </div>
          <div>
            <label className="label">Unit</label>
            <select className="input-field" value={form.unit} onChange={e => set('unit', e.target.value)}>
              {['units', 'g', 'kg', 'ml', 'L', 'lb', 'oz', 'cup', 'pack', 'can', 'bottle', 'bunch', 'dozen'].map(u => (
                <option key={u} value={u}>{u}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Purchase Date *</label>
            <input required type="date" className="input-field" value={form.purchase_date}
              onChange={e => set('purchase_date', e.target.value)} />
          </div>
          <div>
            <label className="label">Expiry Date <span className="text-gray-400 font-normal">(auto-estimated if blank)</span></label>
            <input type="date" className="input-field" value={form.expiry_date}
              onChange={e => set('expiry_date', e.target.value)} />
          </div>
          <div>
            <label className="label">Storage Location</label>
            <select className="input-field" value={form.storage_location}
              onChange={e => set('storage_location', e.target.value)}>
              <option value="refrigerator">🧊 Refrigerator</option>
              <option value="pantry">🏠 Pantry</option>
              <option value="freezer">❄️ Freezer</option>
            </select>
          </div>
          <div>
            <label className="label">Price (optional)</label>
            <input type="number" min="0" step="0.01" className="input-field"
              value={form.price} onChange={e => set('price', e.target.value)} placeholder="0.00" />
          </div>
          <div className="sm:col-span-2">
            <label className="label">Notes</label>
            <textarea className="input-field resize-none" rows="2" value={form.notes}
              onChange={e => set('notes', e.target.value)} placeholder="Any additional notes..." />
          </div>
        </div>

        <div className="flex gap-3 pt-2">
          <button type="submit" disabled={loading} className="btn-primary px-8">
            {loading ? 'Adding...' : 'Add to Inventory'}
          </button>
          <button type="button" onClick={() => navigate(-1)} className="btn-secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}
