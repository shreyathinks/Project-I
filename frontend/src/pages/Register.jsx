import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authApi } from '../api/auth.js'
import { useAuth } from '../context/AuthContext.jsx'
import toast from 'react-hot-toast'

export default function Register() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    email: '', username: '', password: '', full_name: '', household_size: 1,
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    setLoading(true)
    try {
      await authApi.register({ ...form, household_size: Number(form.household_size) })
      await login(form.email, form.password)
      toast.success('Account created! Welcome 🎉')
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const field = (key, label, type = 'text', props = {}) => (
    <div>
      <label className="label">{label}</label>
      <input
        type={type}
        className="input-field"
        value={form[key]}
        onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
        {...props}
      />
    </div>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-green-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🍳</div>
          <h1 className="text-3xl font-bold text-gray-900">Kitchen Intelligence</h1>
          <p className="text-gray-600 mt-2">Create your account</p>
        </div>

        <div className="card shadow-lg">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">Get started</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            {field('full_name', 'Full Name', 'text', { placeholder: 'Jane Smith' })}
            {field('username', 'Username', 'text', { required: true, placeholder: 'janesmith', minLength: 3 })}
            {field('email', 'Email Address', 'email', { required: true, placeholder: 'jane@example.com' })}
            {field('password', 'Password', 'password', { required: true, placeholder: '••••••••' })}
            <div>
              <label className="label">Household Size</label>
              <select
                className="input-field"
                value={form.household_size}
                onChange={e => setForm(f => ({ ...f, household_size: e.target.value }))}
              >
                {[1,2,3,4,5,6].map(n => (
                  <option key={n} value={n}>{n} {n === 1 ? 'person' : 'people'}</option>
                ))}
              </select>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full py-2.5">
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-4">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-600 font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
