import api from './axios.js'

export const recipesApi = {
  list: async (params = {}) => {
    const res = await api.get('/recipes/', { params })
    return res.data
  },
  get: async (id) => {
    const res = await api.get(`/recipes/${id}`)
    return res.data
  },
  recommend: async (data) => {
    const res = await api.post('/recipes/recommend', data)
    return res.data
  },
  loadDataset: async () => {
    const res = await api.post('/recipes/load-dataset')
    return res.data
  },
}

export const dashboardApi = {
  getSummary: async () => {
    const res = await api.get('/dashboard/summary')
    return res.data
  },
  getNotifications: async () => {
    const res = await api.get('/dashboard/notifications')
    return res.data
  },
  markRead: async (id) => {
    await api.post(`/dashboard/notifications/${id}/read`)
  },
  markAllRead: async () => {
    await api.post('/dashboard/notifications/read-all')
  },
}

export const predictionApi = {
  getConsumption: async (itemName) => {
    const res = await api.get(`/prediction/consumption/${encodeURIComponent(itemName)}`)
    return res.data
  },
  getWasteRisk: async () => {
    const res = await api.get('/prediction/waste-risk')
    return res.data
  },
  getShoppingForecast: async () => {
    const res = await api.get('/prediction/shopping-forecast')
    return res.data
  },
}
