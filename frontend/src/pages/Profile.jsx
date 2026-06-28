import { useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { authApi } from '../api/auth.js'
import toast from 'react-hot-toast'

const DIETARY_OPTIONS = ['Vegetarian', 'Vegan', 'Gluten Free', 'Dairy Free', 'High Protein', 'Low Carb', 'Nut Free']

export default function Profile() {
  const { user, updateUser } = useAuth()
  const [form, setForm] = useState({
    full_name: user?.full_name || '',
    household_size: user?.household_size || 1,
  })
  const [dietary, setDietary] = useState(() => {
    try { return JSON.parse(user?.dietary_preferences || '[]') }
    catch { return [] }
  })
  const [saving, setSaving] = useState(false)

  const toggleDietary = (pref) => {
    setDietary(prev => prev.includes(pref) ? prev.filter(p => p !== pref) : [...prev, pref])
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const updated = await authApi.updateProfile({
        full_name: form.full_name,
        household_size: Number(form.household_size),
        dietary_preferences: JSON.stringify(dietary),
      })
      updateUser(updated)
      toast.success('Profile updated!')
    } catch {
      toast.error('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
        <p className="text-sm text-gray-500 mt-1">Manage your account settings</p>
      </div>

      <div className="card space-y-5">
        {/* Avatar */}
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
            {(user?.username || 'U')[0].toUpperCase()}
          </div>
          <div>
            <p className="font-semibold text-gray-900">{user?.username}</p>
            <p className="text-sm text-gray-500">{user?.email}</p>
          </div>
        </div>

        <hr className="border-gray-100" />

        {/* Name */}
        <div>
          <label className="label">Full Name</label>
          <input className="input-field" value={form.full_name}
            onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))} placeholder="Your full name" />
        </div>

        {/* Household size */}
        <div>
          <label className="label">Household Size</label>
          <select className="input-field" value={form.household_size}
            onChange={e => setForm(f => ({ ...f, household_size: e.target.value }))}>
            {[1,2,3,4,5,6].map(n => (
              <option key={n} value={n}>{n} {n === 1 ? 'person' : 'people'}</option>
            ))}
          </select>
        </div>

        {/* Dietary preferences */}
        <div>
          <label className="label">Dietary Preferences</label>
          <div className="flex flex-wrap gap-2 mt-1">
            {DIETARY_OPTIONS.map(pref => (
              <button
                key={pref}
                type="button"
                onClick={() => toggleDietary(pref)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                  dietary.includes(pref)
                    ? 'bg-primary-100 border-primary-400 text-primary-700'
                    : 'bg-white border-gray-300 text-gray-600 hover:border-gray-400'
                }`}
              >
                {pref}
              </button>
            ))}
          </div>
        </div>

        <button onClick={handleSave} disabled={saving} className="btn-primary w-full">
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {/* Account info */}
      <div className="card">
        <h2 className="font-semibold text-gray-800 mb-3">Account Information</h2>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Username</span>
            <span className="font-medium text-gray-700">@{user?.username}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Email</span>
            <span className="font-medium text-gray-700">{user?.email}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Account Status</span>
            <span className={`font-medium ${user?.is_active ? 'text-green-600' : 'text-red-600'}`}>
              {user?.is_active ? '✅ Active' : '❌ Inactive'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
