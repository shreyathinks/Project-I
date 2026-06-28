/**
 * Frontend utility helpers
 */

export const formatDate = (dateStr) => {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

export const getDaysUntil = (dateStr) => {
  if (!dateStr) return null
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const target = new Date(dateStr)
  return Math.round((target - today) / (1000 * 60 * 60 * 24))
}

export const getExpiryStatus = (dateStr) => {
  const days = getDaysUntil(dateStr)
  if (days === null) return 'fresh'
  if (days < 0) return 'expired'
  if (days <= 3) return 'expiring_soon'
  return 'fresh'
}

export const LOCATION_LABELS = {
  refrigerator: '🧊 Refrigerator',
  pantry: '🏠 Pantry',
  freezer: '❄️ Freezer',
}

export const UNIT_OPTIONS = [
  'units', 'g', 'kg', 'ml', 'L', 'lb', 'oz', 'cup',
  'tbsp', 'tsp', 'pack', 'can', 'bottle', 'bunch', 'dozen',
]

export const truncate = (str, n = 40) =>
  str && str.length > n ? str.slice(0, n) + '...' : str

export const capitalize = (str) =>
  str ? str.charAt(0).toUpperCase() + str.slice(1) : ''
