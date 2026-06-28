import api from './axios.js'

export const inventoryApi = {
  list: async (params = {}) => {
    const res = await api.get('/inventory/', { params })
    return res.data
  },
  get: async (id) => {
    const res = await api.get(`/inventory/${id}`)
    return res.data
  },
  create: async (data) => {
    const res = await api.post('/inventory/', data)
    return res.data
  },
  bulkCreate: async (items) => {
    const res = await api.post('/inventory/bulk', items)
    return res.data
  },
  update: async (id, data) => {
    const res = await api.put(`/inventory/${id}`, data)
    return res.data
  },
  delete: async (id) => {
    await api.delete(`/inventory/${id}`)
  },
  consume: async (id, quantity) => {
    const res = await api.post(`/inventory/${id}/consume`, { quantity_consumed: quantity })
    return res.data
  },
  getExpiring: async (days = 3) => {
    const res = await api.get('/inventory/expiring', { params: { days } })
    return res.data
  },
  getCategories: async () => {
    const res = await api.get('/inventory/categories')
    return res.data
  },
  scanReceipt: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/ocr/scan-receipt', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },
  lookupBarcode: async (barcode) => {
    const res = await api.get(`/barcode/lookup/${barcode}`)
    return res.data
  },
}
